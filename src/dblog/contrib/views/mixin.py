from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin)
from django.contrib.auth.views import redirect_to_login
from typing import Dict, Any, List
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.encoding import smart_str
from django.db.models import QuerySet, Model
from django.core.exceptions import ImproperlyConfigured
from contrib.forms.generic import OrderingForm
from contrib.utils import is_valid_uuid, validate_uuids

class MemberMixin(LoginRequiredMixin,
                  UserPassesTestMixin,
                  PermissionRequiredMixin):
    login_url = 'login'
    select_company_url = 'select_company'
    permission_denied_url = 'permission_denied'
    permission_required = ''

    def test_func(self):
        user = self.request.user
        return True

    def get_login_url(self):
        if self.request.user.is_authenticated:
            if True:
                return self.select_company_url
            if not super().has_permission():
                return self.permission_denied_url
        return super().get_login_url()

    def handle_no_permission(self):
        return redirect_to_login(self.request.get_full_path(),
                                 self.get_login_url(),
                                 self.get_redirect_field_name())



class BulkEditMixin:
    """
    Toplu düzenleme olanağına sahip viewlar için mixin.

    :param str `action_param`: Action'ın POST'taki key'i. HTML input name'i.
        Default: 'action'
    :param list[str] `actions`: Zorunlu. Uygulanabilecek action'ların listesi
    :param Model `bulkedit_model`: Toplu işlemlerin yapılcağı model
        Default: models.model (View'da tanımlı olan model)
    :param str `checkbox_object_name`: İşlemlerin uygulanacağı objeleri 
    POST'tan çekmek için name bilgisi. Objelerin HTML checkbox inputlarındaki name'i
        Default: Model adının lowercase'i. Örn: Product modeli için 'product'
        Buna istinaden POST/HTML de beklenen 'selecte_product' olur.
        Ceryancılara iletin.
    """
    action_param = 'action'
    actions = None
    bulkedit_model = None
    checkbox_object_name = None

    def get_bulkedit_model(self):
        if self.bulkedit_model is not None:
            return self.bulkedit_model
        return self.model

    def get_bulkedit_queryset(self, uuids: List[str], manager='publish', **kwargs) -> QuerySet:
        """
        Default olarak publish, yoksa actives managerı kullanılır.
        Değiştirmek için bu methodu manager tanımı yapıp owerride etmeniz kafi.
        Ekstra lookup'ları kwargs içerisine koyabilirsiniz.
        Sonunda super ile parent metodu dönmeyi unutmayın!

        Örnek:
        ```python
        def get_bulkedit_queryset(self, uuids, manager='objects', **kwargs):
            kwargs['company'] = self.request.user.member.selected_company
            return super().get_bulkedit_queryset(uuids, manager, **kwargs)
        ```
        """
        kwargs['uuid__in'] = uuids

        if self.bulkedit_model != self.model:
            return getattr(self.get_bulkedit_model(), manager, 
                self.get_bulkedit_model().actives).filter(**kwargs)

        return self.get_queryset().filter(**kwargs)

    def get_checkbox_object_name(self):
        if self.checkbox_object_name:
            return self.checkbox_object_name
        return smart_str(self.get_bulkedit_model()._meta.object_name.lower())

    def handle_actions(self, request, *args, **kwargs):
        """
        Dinamik gönderme metodu - POST isteklerini 'action' parametresi
        tarafından belirlenen bir metoda iletir. Güvenlik sorunlarından
        kaçınmak için eylemin beyaz listede(self.actions) olması gerekir.
        """
        action = request.POST.get(self.action_param, '').lower()
        if self.actions is None or action not in self.actions:
            return self.reload_page(error=_("Geçersiz aksiyon"))

        uuids = request.POST.getlist(
            f'selected_{self.get_checkbox_object_name()}')

        validate_uuids(uuids)

        if not uuids:
            return self.reload_page(
                error=_("En az bir {} seçimelisiniz".format(smart_str(
                    self.get_bulkedit_model()._meta.verbose_name.title().lower()))))

        objects = self.get_bulkedit_queryset(uuids)
        return getattr(self, action)(request, objects)


class OrderingMixin:
    """
    Queryset'leri olan viewlara ordering hizmeti sunan mütevazi mixin

    :param str ordering_lookup: Url'deki ordering parametresi
        Default: `order_by`. Örn: `/?order_by=latest`
    """
    ordering_form_class = OrderingForm
    ordering_lookup = 'order_by'
    ordering_model = None
    order_by = None
    ordering_queries = None
    ordering = None

    def __init__(self, *args, **kwargs) -> None:
        # Ordering için tanımlanmış model. Default `self.model`
        if self.ordering_model is None:
            self.ordering_model = self.model

        # Modelde tanımlı ordering seçenekleri varsa oradan ilk seçeneği alır.
        if self.order_by is None:
            self.order_by = next(iter(
                next(iter(self.ordering_model.get_ordering_options()), [])
            ), '')

        # Modelde tanımlı oredering seçeneklerinden query listesini çeker
        if self.ordering_queries is None:
            self.ordering_queries = self.model.get_ordering_queries()

        # ordering_queries içerisinden seçilen orderin querysini tanımlar
        if self.ordering is None:
            self.ordering = self.ordering_queries.get(self.order_by, None)

        super(OrderingMixin, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.setdefault('ordering_form', getattr(
            self, 'ordering_form', self.ordering_form_class(self.ordering_model)))

        kwargs.setdefault('order_by', self.order_by)

        return super().get_context_data(**kwargs)

    def apply_order(self, queryset, lookup:str = ordering_lookup) -> QuerySet:
        if lookup in self.request.GET:
            self.ordering_form = self.ordering_form_class(queryset.model,
                                                          self.request.GET)
            if self.ordering_form.is_valid():
                lookup = self.ordering_form.cleaned_data[lookup]
                queryset = queryset.order_by(*self.ordering_queries[lookup])
                self.order_by = lookup
        return queryset
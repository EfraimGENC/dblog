from typing import Dict, Any
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import QuerySet
from contrib.forms.generic import DummyForm, SearchForm
from contrib.views.mixin import MemberMixin
from contrib.views.mixin import BulkEditMixin, OrderingMixin, SearchingMixin


class DblogListView(MemberMixin,
                     FormMixin,
                     OrderingMixin,
                     SearchingMixin,
                     BulkEditMixin,
                     ListView):

    page_url_name = ''
    success_url = None
    form_class = DummyForm

    def setup(self, request, *args, **kwargs):
        # Bu bölümde daha şık bir çalışma yapılabilir. If else leri dizdim ama
        # pek içime sinmedi. Gelişririlebilir.
        # Buradaki temel mantık Djago'dan gelen ve kendi oluşturduğumuz var.lar
        # Bu klasla oluşturulan viewlarda tanımlanmadı ise defaultlar atamak.
        if not hasattr(self, 'model') or self.model is None:
            raise ImproperlyConfigured("'self.model' not defined")
        self.app_label = smart_str(self.model._meta.app_label)
        self.model_name = smart_str(self.model._meta.object_name.lower())

        # Default view permission tanımlıyoruz. Örn: 'catalog.view_gallery'
        if not self.permission_required:
            self.permission_required = f'{self.app_label}.view_{self.model_name}'

        # Template e gidecek queryset var'ını isimlendiriyoruz.
        # Örn: Gallery modeli listingi için 'galleries'.
        # Modelin verbose_name_plural değerinden çekiyoruz.
        if not self.context_object_name:
            self.context_object_name = f'{self.model_name}_list'

        # Sayfanın url nameini tanımlıyoruz. Örn: 'post_list'
        if not self.page_url_name:
            self.page_url_name = f'{self.model_name}_list'

        super().setup(request, *args, **kwargs)

    def get_queryset(self, manager='objects', **extra_lookups) -> QuerySet:
        """
        Default olarak objects managerı kullanılır.
        Değiştirmek için bu methodu manager tanımı yapıp owerride etmeniz kafi.
        Örnek:
        ```python
        def get_queryset(self, manager='mymanager'):
            super().get_queryset(manager)
        ```
        """
        extra_lookups['profile'] = self.request.user
        queryset = getattr(self.model, manager).filter(**extra_lookups)

        # Ordering
        queryset = self.apply_search(self.apply_order(queryset))

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        self.object_list = self.get_queryset()

        kwargs.setdefault('ordering_form', getattr(
            self, 'ordering_form', self.ordering_form_class(self.model)))

        kwargs.setdefault('search_form', getattr(
            self, 'search_form', SearchForm(self.search_param)))

        kwargs.setdefault('order_by', self.order_by)

        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        if not hasattr(self, 'form_class'):
            raise NotImplementedError('form_class tanımlanması zorunludur!')
        return super().get_form_kwargs()

    def get_success_url(self, url_name:str = None, **kwargs) -> str:
        url = url_name or self.success_url or self.page_url_name
        return reverse(url, kwargs=kwargs)

    def form_valid(self, form, **kwargs):
        return HttpResponseRedirect(self.get_success_url(**kwargs))

    def reload_page(self, fragment=None, error=None):
        url = reverse(self.page_url_name)
        if fragment:
            url += '#' + fragment
        if error:
            messages.error(self.request, error)
        return HttpResponseRedirect(url)


class DblogDetailView(MemberMixin,
                       FormMixin,
                       OrderingMixin,
                       BulkEditMixin,
                       DetailView):

    page_url_name = ''
    success_url = None
    form_class = DummyForm

    def setup(self, request, *args, **kwargs):
        if not hasattr(self, 'model') or self.model is None:
            raise ImproperlyConfigured("'self.model' not defined")

        self.app_label = smart_str(self.model._meta.app_label)
        self.model_name = smart_str(self.model._meta.object_name.lower())

        # Default view permission tanımlıyoruz. Örn: 'blog.view_post'
        if not self.permission_required:
            self.permission_required = f'{self.app_label}.view_{self.model_name}'

        # Sayfanın url nameini tanımlıyoruz. Örn: 'post_list'
        if not self.page_url_name:
            self.page_url_name = f'{self.model_name}_detail'

        super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        self.object_list = self.get_queryset()
        return super().get_context_data(**kwargs)

    def get_success_url(self, url_name:str = None, **kwargs) -> str:
        url_name = url_name or self.success_url or self.page_url_name
        return reverse(url_name, kwargs=kwargs)

    def form_valid(self, form, **kwargs):
        return HttpResponseRedirect(self.get_success_url(**kwargs))

    def reload_page(self, fragment=None, error=None):
        url = reverse(self.page_url_name, kwargs={'uuid': self.kwargs['uuid']})
        if fragment:
            url += '#' + fragment
        if error:
            messages.error(self.request, error)
        return HttpResponseRedirect(url)
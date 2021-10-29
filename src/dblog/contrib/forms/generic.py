from django import forms
from django.utils.translation import ugettext_lazy as _


class DummyForm(forms.Form):
    pass


class OrderingForm(forms.Form):
    def __init__(self, model, *args, **kwargs):
        super(OrderingForm, self).__init__(*args, **kwargs)
        self.fields['order_by'].choices = model.get_ordering_choices()

    order_by = forms.ChoiceField(
        label=_('Order'),
        required=True,
    )

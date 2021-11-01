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


class SearchForm(forms.Form):
    def __init__(self, search_param, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields[search_param] = forms.CharField(
                                            label=_('Arama'),
                                            max_length=127,
                                            widget=forms.TextInput(attrs={
                                                'class': 'form-control me-2',
                                                'placeholder': _('Post Bul'),
                                                'aria-label': 'Search',
                                            })
                                        )

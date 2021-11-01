from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Post


class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ("cover", "title", "content", "tags")
        widgets = {
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

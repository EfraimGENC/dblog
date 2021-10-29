from django.shortcuts import render
from django.views.generic import DetailView
from .models import Profile
# Create your views here.
class ProfileDetail(DetailView):
    model = Profile
    template_name='profile_detail.html'
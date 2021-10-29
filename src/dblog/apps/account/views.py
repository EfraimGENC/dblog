from django.shortcuts import render
from contrib.views.generic import DblogListView
from .models import Profile
# Create your views here.
class ProfileDetail(DblogListView):
    model = Profile

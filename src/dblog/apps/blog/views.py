from django.shortcuts import render
from contrib.views.generic import DblogListView
from .models import Post


# Create your views here.
class PostList(DblogListView):
    model = Post

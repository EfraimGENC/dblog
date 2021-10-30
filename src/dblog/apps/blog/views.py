from django.db import models
from django.shortcuts import render
from contrib.views.generic import DblogDetailView, DblogListView
from .models import Post


# Create your views here.
class PostList(DblogListView):
    model = Post


class PostDetail(DblogDetailView):
    model = Post

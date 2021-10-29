from django.contrib import admin
from django.urls import path, include
from apps.account.views import ProfileDetail
from apps.blog.views import PostList

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account', include('apps.account.urls')),
    path("blog/", PostList.as_view(), name="post_list"),
    path("@<slug:username>/", ProfileDetail.as_view(), name="profile")
]

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from apps.account.views import ProfileDetail
from apps.blog.views import PostList, PostDetail
from .api import urlpatterns as api_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include((api_urls, 'api'))),
    path("blog/", PostList.as_view(), name="post_list"),
    path("blog/<uuid:uuid>", PostDetail.as_view(), name="post_detail"),
    path("@<slug:username>/", ProfileDetail.as_view(), name="profile_detail")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

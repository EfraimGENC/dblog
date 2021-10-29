from django.contrib import admin
from django.urls import path, include
from apps.account.views import ProfileDetail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account', include('apps.account.urls')),
    path("@<slug:username>/", ProfileDetail.as_view(), name="profile")
]

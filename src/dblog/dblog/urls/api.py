from rest_framework.routers import DefaultRouter
from apps.blog.api.views import PostViewSet


router = DefaultRouter()
router.register('blog', PostViewSet, basename='post')
urlpatterns = router.urls
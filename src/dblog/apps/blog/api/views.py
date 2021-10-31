import django_filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from django_filters.rest_framework import FilterSet
from django.shortcuts import get_object_or_404
from ..models import Post
from .serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):

    class Filter(FilterSet):
        username = django_filters.CharFilter(field_name="profile__username",
                                             lookup_expr='exact')

        class Meta:
            model = Post
            fields = {
                'uuid': ['exact'],
                'title': ['contains'],
            }


    model = Post
    serializer_class = PostSerializer
    lookup_field = 'uuid'
    filterset_class = Filter
    ordering = ['-created_at', '-id']
    ordering_fields = ['created_at', 'id', 'title', 'profile']
    search_fields = ['title', 'profile__username']

    def get_queryset(self, manager='objects', **kwargs):
        return getattr(self.model, manager).filter(**kwargs)

    def get_object(self, manager='objects', **kwargs):
        posts = self.filter_queryset(self.get_queryset(manager))

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        post = get_object_or_404(posts, **filter_kwargs)

        self.check_object_permissions(self.request, post)

        return post

    def get_serializer_class(self):
        if not self.action in ['list', 'retrieve']:
            return self.serializer_class
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = []
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user)

    def perform_update(self, serializer):
        serializer.save(profile=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    # Extra Actions

    @action(detail=False, methods=['get'], name='My Custom Action')
    def my_custom_action(self, request):
        posts = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @my_custom_action.mapping.post
    def add_my_custom_action(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

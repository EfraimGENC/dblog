import django_filters
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from django_filters.rest_framework import FilterSet
from django.shortcuts import get_object_or_404
from rest_framework.serializers import Serializer
from ..models import Post, Tag
from .serializers import TagSerializer, PostSerializer, ProfileSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

class PostViewSet(viewsets.ModelViewSet):

    class Filter(FilterSet):
        # price__gt = django_filters.NumberFilter(field_name='price',
        #                                         lookup_expr='gt')
        # price__lt = django_filters.NumberFilter(field_name='price',
        #                                         lookup_expr='lt')
        username = django_filters.CharFilter(field_name="profile__username",
                                             lookup_expr='exact')

        class Meta:
            model = Post
            fields = {
                'uuid': ['exact'],
                'title': ['exact'],
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
        if self.action in ['list']:
            return self.serializer_class
        elif self.action in ['create']:
            return self.serializer_class
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return self.serializer_class
        elif self.action in ['destroy']:
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

    @action(detail=False, methods=['get'], name='Koko Jambo')
    def koko_jambo(self, request):
        posts = self.get_queryset()
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @koko_jambo.mapping.post
    def add_koko_jambo(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    model = User
    queryset = model.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = ProfileSerializer
    ordering = ['-id']
    ordering_fields = ['id', 'username']
    search_fields = ['first_name', 'last_name', 'username', 'email']


class TagViewSet(viewsets.ModelViewSet):
    model = Tag
    queryset = model.objects.all()
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = TagSerializer
    ordering = ['-id']
    ordering_fields = ['id', 'name']
    search_fields = ['name', 'uuid']

    def get_queryset(self, manager='objects', **kwargs):
        kwargs['product__in'] = Post.objects.filter(user=self.request.user)
        return getattr(self.model, manager).filter(**kwargs)

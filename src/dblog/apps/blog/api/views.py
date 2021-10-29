import django_filters
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from django_filters.rest_framework import FilterSet
from django.shortcuts import get_object_or_404
from rest_framework.serializers import Serializer
from ..models import Product, ProductColor
from .serializers import ProductColorSerializer, ProductSerializer, UserSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

class ProductViewSet(viewsets.ModelViewSet):

    class Filter(FilterSet):
        price__gt = django_filters.NumberFilter(field_name='price',
                                                lookup_expr='gt')
        price__lt = django_filters.NumberFilter(field_name='price',
                                                lookup_expr='lt')
        username = django_filters.CharFilter(field_name="user__username",
                                             lookup_expr='exact')

        class Meta:
            model = Product
            fields = {
                'id': ['exact'],
                'uuid': ['exact'],
                'name': ['exact'],
                'price': ['exact'],
            }


    model = Product
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = ProductSerializer
    lookup_field = 'uuid'
    filterset_class = Filter
    ordering = ['-created_at', '-id']
    ordering_fields = ['created_at', 'id', 'name', 'user']
    search_fields = ['name', 'user__username', 'price']

    def get_queryset(self, manager='objects', **kwargs):
        kwargs['user'] = self.request.user
        return getattr(self.model, manager).filter(**kwargs)

    def get_object(self, manager='objects', **kwargs):
        products = self.filter_queryset(self.get_queryset(manager))

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        filter_kwargs['user'] = self.request.user

        product = get_object_or_404(products, **filter_kwargs)

        self.check_object_permissions(self.request, product)

        return product

    def get_serializer_class(self):
        print(self.action, '<<<<<<<<<<<<<<<<<<<<<<<cc')
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
        if self.action in ['list']:
            self.permission_classes += []
        else:
            self.permission_classes += []
        return super().get_permissions()

    # Base Methods

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, fields=('user', 'name', 'price', 'colors'))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, fields=('user', 'name', 'price', 'colors'))
        return Response(serializer.data)

    # def update(self, request, uuid=None):
    #     product = self.get_object(uuid)
    #     serializer = self.get_serializer(instance=product, data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save(user=request.user)
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    # def partial_update(self, request, uuid=None):
    #     product = self.get_object(uuid)
    #     serializer = self.get_serializer(instance=product, data=request.data, partial=True)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save(user=request.user)
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    # def destroy(self, request, uuid=None):
    #     product = self.get_object(uuid)
    #     self.perform_destroy(product)
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    # Extra Actions

    @action(detail=False, methods=['get'], name='Koko Jambo')
    def koko_jambo(self, request):
        products = self.get_queryset()
        serializer = self.get_serializer(products, many=True)
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
    serializer_class = UserSerializer
    ordering = ['-id']
    ordering_fields = ['id', 'username']
    search_fields = ['first_name', 'last_name', 'username', 'email']


class ProductColorViewSet(viewsets.ModelViewSet):
    model = ProductColor
    queryset = model.objects.all()
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = ProductColorSerializer
    ordering = ['-id']
    ordering_fields = ['id', 'name']
    search_fields = ['name', 'uuid']

    def get_queryset(self, manager='objects', **kwargs):
        kwargs['product__in'] = Product.objects.filter(user=self.request.user)
        return getattr(self.model, manager).filter(**kwargs)

from django.db.models import fields
from rest_framework import serializers
from django.db import transaction
from ..models import Post, Tag
from django.contrib.auth import get_user_model
Profile = get_user_model()


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if self.context.get('request', None):
            # Get fields from url params "api/?fields=id,name,etc"
            fields = self.context['request'].query_params.get('fields', None)
            fields = fields.split(',') if fields is not None else None

        if fields is not None and fields != ['']:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProfileSerializer(DynamicFieldsModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='profile_detail',
        lookup_field='username'
    )

    class Meta:
        model = Profile
        fields = ['uuid', 'username', 'password', 'first_name', 'last_name', 'email', 'url']
        write_only_fields = ('password',)


class TagSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Tag
        fields = ('uuid', 'name')


class PostSerializer(DynamicFieldsModelSerializer):

    tags = TagSerializer(many=True, fields=['name'])
    profile = ProfileSerializer(fields=['uuid', 'username', 'url'], read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='api:post-detail',
        lookup_field='uuid'
    )

    class Meta:
        model = Post
        fields = ('uuid', 'title', 'cover', 'content', 'created_at', 'updated_at', 'profile', 'tags', 'url')
        read_only_fields = ('profile',)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')

        product = super().create(validated_data)

        for tag in tags:
            product.tags.add(Tag.objects.get_or_create(**tag)[0])

        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        product = super().update(instance, validated_data)
        return product

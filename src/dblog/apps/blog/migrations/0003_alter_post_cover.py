# Generated by Django 3.2.8 on 2021-10-29 20:30

import apps.blog.models
from django.db import migrations
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_post_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='cover',
            field=imagekit.models.fields.ProcessedImageField(blank=True, default='', null=True, upload_to=apps.blog.models.Post.handle_cover_file, verbose_name='Cover'),
        ),
    ]

# Generated by Django 3.2.8 on 2021-10-29 20:17

import apps.blog.models
from django.db import migrations
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='cover',
            field=imagekit.models.fields.ProcessedImageField(default='', upload_to=apps.blog.models.Post.handle_cover_file, verbose_name='Cover'),
        ),
    ]
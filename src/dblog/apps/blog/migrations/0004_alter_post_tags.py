# Generated by Django 3.2.8 on 2021-10-29 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_alter_post_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, to='blog.Tag', verbose_name='Etiketler'),
        ),
    ]

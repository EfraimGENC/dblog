from django.db import models
from django.db.models import F
from contrib.models.base import BaseModel
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect, reverse
from django.conf import settings
from os.path import splitext
import uuid
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class Tag(BaseModel):

    name = models.CharField(_('Etiket'), max_length=127)

    class Meta:
        verbose_name = _('Etiket')
        verbose_name_plural = _('Etiketler')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tag_detail", kwargs={"uuid": self.uuid})


class Post(BaseModel):
    def handle_cover_file(instance, filename):
        extension = splitext(filename)[1].lower()
        rondom = str(uuid.uuid4()).lower()
        return 'cover/{post}-{rondom}{extension}'.format(
            post=instance.uuid,
            rondom=rondom[:8],
            extension=extension)

    profile = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)

    cover = ProcessedImageField(verbose_name=_("Cover"),
                                upload_to=handle_cover_file,
                                default='',
                                processors=[ResizeToFill(1080, 1080)],
                                format='JPEG',
                                options={'quality': 80},
                                null=True,
                                blank=True)

    title = models.CharField(_('Başlık'), max_length=255)
    content = models.TextField(_('İçerik'))
    tags = models.ManyToManyField("blog.Tag",
                                  verbose_name=_('Etiketler'),
                                  blank=True)

    ORDERING_OPTIONS = [
        (
            'profile',
            _('Profile'),
            (F('profile').desc(), F('created_at').desc(), F('id').desc())
        ),
    ]

    class Meta(BaseModel.Meta):
        verbose_name = _("Gönderi")
        verbose_name_plural = _("Gönderi")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"uuid": self.uuid})

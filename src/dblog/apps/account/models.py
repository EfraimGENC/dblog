from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect, reverse
from django.conf import settings
from os.path import splitext
import uuid
from phonenumber_field.modelfields import PhoneNumberField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from contrib.models.base import BaseModel


class Profile(AbstractUser, BaseModel):

    def handle_avatar_file(instance, filename):
        extension = splitext(filename)[1].lower()
        rondom = str(uuid.uuid4()).lower()
        return 'avatar/{user}-{rondom}{extension}'.format(
            user=instance.id,
            rondom=rondom,
            extension=extension)

    avatar = ProcessedImageField(
        verbose_name=_("Profile Picture"),
        upload_to=handle_avatar_file,
        default='',
        processors=[ResizeToFill(80, 80)],
        format='JPEG',
        options={'quality': 70},
        null=False,
        blank=False,
    )

    phone = PhoneNumberField(
        _('Phone'),
        null=False,
        blank=False,
    )

    location = models.CharField(
        _('Location'),
        max_length=30,
        null=True,
        blank=True
    )

    birthday = models.DateField(
        _('Birthday'),
        null=True,
        blank=True
    )

    language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE
    )

    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return "{} {}".format(self.first_name, self.last_name)
        else:
            return self.username

    @full_name.setter
    def full_name(self, value):
        """
        Full name in boşluktan sonraki son kelimesini last_name,
        öncesini first_name e kaydeder.
        """
        cleaned_name = " ".join(value.split()) # Başındaki ve sondaki boşlukları kaldırır
        names = cleaned_name.split(' ')
        if len(names) > 1:
            self.first_name = " ".join(names[:-1])
            self.last_name = "".join(names[-1])
        else:
            self.first_name = "".join(names[0])
            self.last_name = ''

    def get_absolute_url(self):
        return reverse("profile_detail", kwargs={"username": self.username})

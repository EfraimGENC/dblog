from uuid import UUID
import string
from typing import Iterable
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.utils.text import slugify
import string


def generate_random_slug(length: int,
                         letters: bool = True,
                         digits: bool = True,
                         extra: str = None):
    """
    Returns random slugify string.
    Default: ascii_letters + digits
    If allowed_chars is defined, ignore letters and digits
    """

    allowed_chars = str()
    if letters:
        allowed_chars += string.ascii_uppercase
    if digits:
        allowed_chars += string.digits
    if extra is not None:
        allowed_chars += extra

    allowed_chars = allowed_chars or (string.ascii_lowercasei + string.digits)

    return slugify(
        get_random_string(length=length, allowed_chars=allowed_chars))

def is_valid_uuid(uuid: str, version: int = 4) -> bool:
    try:
        UUID(hex=uuid, version=version)
        return True
    except ValueError:
        return False

def validate_uuids(uuids: Iterable[str]) -> None:
    for uuid in uuids:
        if not is_valid_uuid(uuid):
            raise ValidationError(_('Invalid UUID'))

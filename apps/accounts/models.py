from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import BaseUserManager
from apps.common.models import BaseModel


class BaseUser(BaseModel, AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=32,
        unique=True,
        help_text=_(
            "Required. 32 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    phone_number = models.CharField(max_length=11, unique=True, verbose_name=_('phone number'))
    avatar_image = models.CharField(verbose_name=_("avatar image"), max_length=240, blank=True, null=True)
    last_image_update = models.DateTimeField(verbose_name=_("last image update"), blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))
    is_admin = models.BooleanField(default=False, verbose_name=_('is admin'))

    objects = BaseUserManager()

    USERNAME_FIELD = 'phone_number'

    REQUIRED_FIELDS = ("username",)

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin

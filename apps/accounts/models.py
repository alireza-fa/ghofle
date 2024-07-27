from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.managers import BaseUserManager
from apps.common.models import BaseModel, File


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
    avatar_image = models.ForeignKey(File, on_delete=models.CASCADE, related_name="avatar_images",
                                     null=True, blank=True, verbose_name=_("avatar image"))
    avatar_image_filename = models.CharField(max_length=64, null=True, blank=True, editable=False)
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


class UserRole(BaseModel):
    DEFAULT = 1
    ADMIN = 2
    ALL_ROLES = [DEFAULT, ADMIN]

    ROLE_CHOICES = (
        (DEFAULT, _("default")),
        (ADMIN, _("admin")),
    )

    user = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name='roles', verbose_name=_('user'))
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, verbose_name=_("role"))

    def __str__(self):
        return f'{self.user} - {self.role}'

    class Meta:
        verbose_name = _("User role")
        verbose_name_plural = _("User roles")
        unique_together = [["user", "role"]]

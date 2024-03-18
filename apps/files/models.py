from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel

User = get_user_model()


class File(BaseModel):
    filename = models.CharField(max_length=64, verbose_name=_("filename"))
    size = models.IntegerField(max_length=32, verbose_name=_("size"))
    format = models.CharField(max_length=10, verbose_name=_("format"))
    expire_at = models.DateTimeField(verbose_name=_("expire at"))

    class Meta:
        verbose_name = _("Storage")
        verbose_name_plural = _("Storages")

    def __str__(self):
        return f"{self.filename} - {self.size}"


class PadLock(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="own_padlocks", verbose_name=_("owner"))
    title = models.CharField(max_length=120, verbose_name=_("title"))
    description = models.CharField(max_length=1024, verbose_name=_("description"))
    thumbnail = models.ForeignKey(File, models.SET_NULL, null=True, blank=True, verbose_name=_("thumbnail"),
                                  related_name="thumbnails")
    file = models.ForeignKey(File, models.SET_NULL, null=True, blank=True, verbose_name=_("file"), related_name="files")
    is_active = models.BooleanField(default=False, verbose_name=_("is active"))
    review_active = models.BooleanField(default=True, verbose_name=_("active review"))
    price = models.IntegerField(verbose_name=_("price"))
    is_auction = models.BooleanField(default=False, verbose_name=_("is auction"))
    is_private = models.BooleanField(default=False, verbose_name=_("is private"))
    limit_sell = models.IntegerField(verbose_name=_("limit sell"), null=True, blank=True)

    class Meta:
        verbose_name = _("PadLock")
        verbose_name_plural = _("PadLocks")

    def __str__(self):
        return f"{self.owner} - {self.title}"


class PadLockUserAccess(BaseModel):
    padlock = models.ForeignKey(PadLock, on_delete=models.CASCADE, verbose_name=_("padlock"),
                                related_name="user_accesses")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("user"), related_name="padlock_accesses")

    class Meta:
        verbose_name = _("PadLockUserAccess")
        verbose_name_plural = _("PadLockUserAccesses")

    def __str__(self):
        return f"{self.user} - {self.padlock}"


class PadLockUser(BaseModel):
    padlock = models.ForeignKey(PadLock, on_delete=models.CASCADE, verbose_name=_("padlock"), related_name="users")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("user"), related_name=_("padlocks"))

    class Meta:
        verbose_name = _("PadlockUser")
        verbose_name_plural = _("PadlockUsers")

    def __str__(self):
        return f"{self.user} - {self.padlock}"
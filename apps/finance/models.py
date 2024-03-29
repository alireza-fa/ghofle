from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from apps.common.models import BaseModel

User = get_user_model()


class Gateway(BaseModel):
    ZIBAL = 1

    NAME_CHOICES = (
        ZIBAL, _("zibal")
    )

    name = models.PositiveSmallIntegerField(choices=NAME_CHOICES, verbose_name=_("name"))
    authorization = models.CharField(max_length=240, verbose_name=_("authorization"))
    is_active = models.BooleanField(default=False, verbose_name=_("is active"))

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("payments")

    def __str__(self):
        return f"{self.name} - {self.is_active}"


class Payment(BaseModel):
    gateway = models.ForeignKey(Gateway, on_delete=models.CASCADE, related_name="payments", verbose_name=_("gateway"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments", verbose_name=_("user"))
    amount = models.PositiveIntegerField(verbose_name=_("amount"))
    description = models.CharField(max_length=120, verbose_name=_("description"))
    track_id = models.PositiveIntegerField(verbose_name=_("track id"))
    status = models.BooleanField(default=False, verbose_name=_("status"))
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("paid at"))
    card_number = models.CharField(max_length=25, verbose_name=_("card number"))
    ref_number = models.CharField(max_length=25, verbose_name=_("ref number"))
    device_name = models.CharField(max_length=120, verbose_name=_("device name"))
    ip_address = models.CharField(max_length=126, verbose_name=_("ip address"))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"{self.user} - {self.description} - {self.status}"

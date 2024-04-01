from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from apps.common.models import BaseModel

User = get_user_model()


class Gateway(BaseModel):
    ZIBAL = 1

    NAME_CHOICES = (
        (ZIBAL, _("zibal")),
    )

    name = models.PositiveSmallIntegerField(choices=NAME_CHOICES, verbose_name=_("name"))
    authorization = models.CharField(max_length=240, verbose_name=_("authorization"))
    callback_url = models.CharField(max_length=120, verbose_name=_("callback url"))
    is_active = models.BooleanField(default=False, verbose_name=_("is active"))

    class Meta:
        verbose_name = _("Gateway")
        verbose_name_plural = _("Gateways")

    def __str__(self):
        return f"{self.name} - {self.is_active}"


class Payment(BaseModel):
    PADLOCK = 1
    PAYMENT_CHOICES = (
        (PADLOCK, _("padlock")),
    )

    gateway = models.ForeignKey(Gateway, on_delete=models.CASCADE, related_name="payments", verbose_name=_("gateway"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments", verbose_name=_("user"))
    payment_type = models.PositiveSmallIntegerField(choices=PAYMENT_CHOICES, verbose_name=_("payment type"))
    amount = models.PositiveIntegerField(verbose_name=_("amount"))
    description = models.CharField(max_length=120, verbose_name=_("description"))
    track_id = models.PositiveBigIntegerField(db_index=True, verbose_name=_("track id"))
    status = models.BooleanField(default=False, verbose_name=_("status"))
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("paid at"))
    card_number = models.CharField(max_length=25, null=True, blank=True, verbose_name=_("card number"))
    ref_number = models.CharField(max_length=25, null=True, blank=True, verbose_name=_("ref number"))
    device_name = models.CharField(max_length=120, null=True, blank=True, verbose_name=_("device name"))
    ip_address = models.CharField(max_length=126, null=True, blank=True, verbose_name=_("ip address"))

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")

    def __str__(self):
        return f"{self.user} - {self.description} - {self.status}"

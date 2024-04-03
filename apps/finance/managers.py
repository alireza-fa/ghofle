from django.db.models import Manager


class PaymentManager(Manager):

    def get_queryset(self):
        return super().get_queryset().select_related("gateway", "user")

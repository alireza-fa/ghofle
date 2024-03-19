from django.db.models.manager import BaseManager


class PadlockManager(BaseManager):

    def get_queryset(self):
        return super().get_queryset().select_related("owner")

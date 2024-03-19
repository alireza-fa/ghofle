from django.db.models import Manager


class PadlockManager(Manager):

    def get_queryset(self):
        return super().get_queryset().select_related("owner", "file", "thumbnail")


class PadlockUserManager(Manager):

    def get_queryset(self):
        return super().get_queryset().select_related("padlock", "user", "padlock__file")

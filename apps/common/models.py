from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class File(BaseModel):
    IMAGE = 1
    MOVIE = 2
    DOCUMENT = 3

    FILE_TYPE_CHOICES = (
        (IMAGE, _("image")),
        (MOVIE, _("Movie")),
        (DOCUMENT, _("pdf")),
    )

    file_type = models.PositiveSmallIntegerField(choices=FILE_TYPE_CHOICES, verbose_name=_("file type"))
    filename = models.CharField(max_length=64, verbose_name="filename", unique=True)
    size = models.IntegerField(verbose_name=_("size"))
    expire_at = models.DateTimeField(verbose_name=_("expire at"), null=True, blank=True)

    class Meta:
        verbose_name = _("Storage")
        verbose_name_plural = _("Storages")

    def __str__(self):
        return f"{self.filename} - {self.size}"

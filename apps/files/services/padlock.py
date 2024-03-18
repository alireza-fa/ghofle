from datetime import timedelta
from typing import Dict

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.common.storage import put_file
from apps.files.models import Padlock, File
from apps.pkg.logger.logger import new_logger
from apps.common.logger import properties_with_user

log = new_logger()
User = get_user_model()


def create_file(*, file: object, extra: Dict) -> File:
    f = put_file(file=file, log_properties=extra)
    file = File()
    file.filename = f["filename"]
    file.size = f["size"]
    file.expire_at = timezone.now() + timedelta(days=30)
    file.save()
    return file


def create_padlock(*, user: User, title: str, description: str, price: int, file: object,
                   thumbnail: object | None = None, review_active: bool = True) -> Padlock:
    properties = {
        **properties_with_user(user=user, extra={})
    }

    padlock = Padlock.objects.create(owner=user, title=title, description=description,
                                     review_active=review_active, price=price)

    if thumbnail:
        f = create_file(file=thumbnail, extra=properties)
        padlock.thumbnail = f

    f = create_file(file=file, extra=properties)
    padlock.file = f

    padlock.save()
    return padlock

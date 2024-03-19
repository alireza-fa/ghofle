from datetime import timedelta
from typing import Dict

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.utils import timezone

from apps.common.storage import put_file
from apps.files.exceptions import RichPadlockLimit, PadlockDoesNotExist
from apps.files.models import Padlock, File
from apps.pkg.logger import category
from apps.pkg.logger.logger import new_logger
from apps.common.logger import properties_with_user
from apps.utils import client

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


def create_padlock(*, request: HttpRequest, title: str, description: str, price: int, file: object,
                   thumbnail: object | None = None, review_active: bool = True) -> Padlock:
    user = request.user
    client_info = client.get_client_info(request=request)

    if Padlock.objects.filter(owner=user, checked=False).count() >= 5:
        raise RichPadlockLimit

    properties = {
        **properties_with_user(user=user, extra=client_info)
    }

    padlock = Padlock.objects.create(owner=user, title=title, description=description,
                                     review_active=review_active, price=price)

    if thumbnail:
        f = create_file(file=thumbnail, extra=properties)
        padlock.thumbnail = f

    f = create_file(file=file, extra=properties)
    padlock.file = f

    padlock.save()
    log.error(message=f"create a new padlock for user {user.username}",
              category=category.PADLOCK, sub_category=category.CREATE_PADLOCK, properties=properties)
    return padlock


def delete_padlock(*, request: HttpRequest, padlock_id):
    user = request.user

    try:
        padlock = Padlock.objects.get(owner=user, id=padlock_id, is_deleted=False)
    except Padlock.DoesNotExist:
        raise PadlockDoesNotExist

    padlock.is_deleted = True
    padlock.save()

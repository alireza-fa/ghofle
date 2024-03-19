from django.contrib.auth import get_user_model
from django.http import HttpRequest

from ..exceptions import PadlockDoesNotExist, AccessDeniedPadlockFile
from ..models import Padlock, PadLockUser
from apps.common.logger import properties_with_user
from apps.pkg.logger import category
from apps.pkg.logger.logger import new_logger
from apps.utils import client
from apps.pkg.storage.storage import get_storage

User = get_user_model()
log = new_logger()
storage = get_storage()


def get_user_own_padlocks(user: User):
    return Padlock.objects.filter(owner=user)


def get_padlock(padlock_id: int):
    try:
        return Padlock.objects.get(id=padlock_id, is_deleted=False, is_active=True)
    except Padlock.DoesNotExist:
        log.error(message="Padlock with id does not exist", category=category.POSTGRESQL, sub_category=category.SELECT)
        raise PadlockDoesNotExist


def open_padlock_file(request: HttpRequest, padlock_id: int):
    user = request.user
    properties = properties_with_user(user=user, extra=client.get_client_info(request=request))

    try:
        padlock_user = PadLockUser.objects.get(user__id=user.id, padlock__id=padlock_id, padlock__is_active=True)
    except PadLockUser.DoesNotExist:
        log.error(message=f"PadlockUser with id: {padlock_id} does not exist",
                  category=category.POSTGRESQL, sub_category=category.SELECT, properties=properties)
        raise PadlockDoesNotExist

    if padlock_user.use_time >= 3:
        raise AccessDeniedPadlockFile

    padlock_user.use_time += 1
    log.info(message=f"user {user.username} open padlock {padlock_id} file",
             category=category.PADLOCK, sub_category=category.OPEN_PADLOCK_FILE, properties=properties)
    padlock_user.save()

    return storage.get_file_url(filename=padlock_user.padlock.file.filename)

from django.contrib.auth import get_user_model

from ..exceptions import PadlockDoesNotExist
from ..models import Padlock
from apps.pkg.logger import category
from apps.pkg.logger.logger import new_logger
from apps.pkg.storage.storage import get_storage

User = get_user_model()
log = new_logger()
storage = get_storage()


def get_user_own_padlocks(user: User) -> Padlock:
    return Padlock.objects.filter(owner=user)


def get_padlock(padlock_id: int) -> Padlock:
    return Padlock.objects.get(id=padlock_id, is_deleted=False, is_active=True)


def get_user_buy_padlocks(user: User):
    return Padlock.objects.filter(is_active=True, users__user=user).distinct()

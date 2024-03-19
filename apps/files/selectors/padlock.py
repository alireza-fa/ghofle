from django.contrib.auth import get_user_model

from ..exceptions import PadlockDoesNotExist
from ..models import Padlock

User = get_user_model()


def get_user_own_padlocks(user: User):
    return Padlock.objects.filter(owner=user)


def get_padlock(padlock_id: int):
    try:
        return Padlock.objects.get(id=padlock_id, is_deleted=False, is_active=True)
    except Padlock.DoesNotExist:
        raise PadlockDoesNotExist

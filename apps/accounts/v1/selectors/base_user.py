from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError

from apps.accounts.exceptions import UserConflictErr
from apps.accounts.models import UserRole
from pkg.logger.logger import new_logger
from pkg.logger import category

log = new_logger()
User = get_user_model()


def get_user_by_phone_number(phone_number: str) -> User:
    try:
        user = User.objects.get(phone_number=phone_number)
        log.info(message=f"select user {user.username} ",
                 category=category.POSTGRESQL, sub_category=category.SELECT,
                 properties={"PhoneNumber": phone_number})
    except User.DoesNotExist:
        log.error(message=f"user with phone number {phone_number} not found",
                  category=category.POSTGRESQL, sub_category=category.SELECT,
                  properties={})
        raise User.DoesNotExist

    return user


@transaction.atomic
def create_new_user(username: str, phone_number: str, is_active: bool = True,
                    is_admin: bool = False, is_superuser: bool = False) -> User:
    try:
        user = User.objects.create(
            username=username,
            phone_number=phone_number,
            is_active=is_active,
            is_admin=is_admin,
            is_superuser=is_superuser
        )
    except IntegrityError as err:
        raise UserConflictErr(str(err))

    user.roles.create(role=UserRole.DEFAULT)

    if is_admin:
        user.roles.create(role=UserRole.ADMIN)

    return user

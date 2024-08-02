from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError

from apps.accounts.exceptions import UserConflictErr
from apps.accounts.models import UserRole
from apps.api import response_code
from pkg.logger.logger import new_logger
from pkg.logger import category
from pkg.richerror.error import RichError

log = new_logger()
User = get_user_model()


def get_user_by_phone_number(phone_number: str) -> User:
    op = "accounts.selectors.base_user.get_user_by_phone_number"

    try:
        user = User.objects.get(phone_number=phone_number)
        log.info(message=f"select user {user.username} ",
                 category=category.POSTGRESQL, sub_category=category.SELECT,
                 properties={"PhoneNumber": phone_number})
    except User.DoesNotExist as ex:
        log.error(message=f"user with phone number {phone_number} not found",
                  category=category.POSTGRESQL, sub_category=category.SELECT,
                  properties={})

        raise RichError(operation=op, message="user does not exists", code=response_code.USER_NOT_FOUND, error=ex)

    return user


def get_user_by_id(user_id: int) -> User:
    return User.objects.get(id=user_id)


@transaction.atomic
def create_new_user(username: str, phone_number: str, is_active: bool = True,
                    is_admin: bool = False, is_superuser: bool = False) -> User:
    op = "accounts.selectors.base_user.create_new_user"

    try:
        user = User.objects.create(
            username=username,
            phone_number=phone_number,
            is_active=is_active,
            is_admin=is_admin,
            is_superuser=is_superuser
        )
    except IntegrityError as ex:
        raise RichError(operation=op, message="user conflict", code=response_code.USER_EXIST, error=ex)

    user.roles.create(role=UserRole.DEFAULT)

    if is_admin:
        user.roles.create(role=UserRole.ADMIN)

    return user

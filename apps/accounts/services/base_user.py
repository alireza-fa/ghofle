from django.contrib.auth import get_user_model
from django.db import transaction

from apps.pkg.logger.logger import new_logger
from apps.pkg.logger import category

User = get_user_model()
log = new_logger()


@transaction.atomic
def create_base_user(*, username, phone_number,
                     is_active=True, is_admin=False, password=None) -> User:
    user = User(
        username=username,
        phone_number=phone_number,
        is_active=is_active,
        is_admin=is_admin,
    )

    if password is not None:
        user.set_password(password)
    else:
        user.set_unusable_password()

    user.full_clean()
    user.save()
    log.info(message=f"user with username {username} created",
             category=category.POSTGRESQL, sub_category=category.INSERT,
             properties={"Username": username, "PhoneNumber": phone_number, "password": password})

    return user

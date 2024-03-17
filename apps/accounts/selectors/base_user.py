from django.contrib.auth import get_user_model

from apps.common.exceptions import UserNotFound
from apps.pkg.logger.logger import new_logger
from apps.pkg.logger import category

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
        raise UserNotFound

    return user


def get_user_by_username(username: str) -> User:
    try:
        user = User.objects.get(username=username)
        log.info(message=f"select user {user.username} ",
                 category=category.POSTGRESQL, sub_category=category.SELECT,
                 properties={})
    except User.DoesNotExist:
        log.error(message=f"user with username {username} not found",
                  category=category.POSTGRESQL, sub_category=category.SELECT,
                  properties={"Username": username})
        raise UserNotFound

    return user


def create_base_user(username: str, phone_number: str, password: str) -> User:
    user = User.objects.create_user(username=username, phone_number=phone_number, password=password)
    log.info(message=f"user with username {username} created",
             category=category.POSTGRESQL, sub_category=category.INSERT,
             properties={"Username": username, "PhoneNumber": phone_number, "password": password})
    return user

from django.contrib.auth import get_user_model

from apps.pkg.logger.logger import new_logger
from apps.pkg.logger import category

User = get_user_model()
log = new_logger()


def create_base_user(username: str, phone_number: str, password: str) -> User:
    user = User.objects.create_user(username=username, phone_number=phone_number, password=password)
    log.info(message=f"user with username {username} created",
             category=category.POSTGRESQL, sub_category=category.INSERT,
             properties={"Username": username, "PhoneNumber": phone_number, "password": password})
    return user

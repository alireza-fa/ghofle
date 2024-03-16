from django.contrib.auth import get_user_model

from typing import Dict

from apps.pkg.logger.base import Log


def properties_with_user(user: get_user_model(), extra: Dict):
    return {
        **extra,
        "UserId": user.id,
        "Username": user.username,
        "PhoneNumber": user.phone_number
    }

from django.contrib.auth import get_user_model

from typing import Dict


def properties_with_user(user: get_user_model(), extra: Dict):
    return {
        **extra,
        "UserId": user.id,
        "Username": user.username,
        "PhoneNumber": user.phone_number
    }

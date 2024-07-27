from datetime import datetime

from django.contrib.auth import get_user_model

from typing import Dict

from apps.utils.client import IP_ADDRESS, DEVICE_NAME


def get_default_log_properties(client_info: Dict, **kwargs) -> Dict:
    properties = {
        "IpAddress": client_info[IP_ADDRESS],
        "DeviceName": client_info[DEVICE_NAME],
        **kwargs
    }
    for key, value in kwargs.items():
        if type(value) in [str, None, bool, datetime]:
            properties[key] = value

    return properties


def properties_with_user(user: get_user_model(), extra: Dict):
    return {
        **extra,
        "UserId": user.id,
        "Username": user.username,
        "PhoneNumber": user.phone_number
    }


def get_default_log_properties_with_user(client_info: Dict, user: get_user_model(), **kwargs) -> dict:
    properties = {
        "IpAddress": client_info[IP_ADDRESS],
        "DeviceName": client_info[DEVICE_NAME],
        "UserId": user.id,
        "PhoneNumber": user.phone_number,
    }

    for key, value in kwargs.items():
        if type(value) in [str, None, bool, datetime]:
            properties[key] = value

    return properties

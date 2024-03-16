from typing import Dict

from django.contrib.auth import get_user_model
from django.http import HttpRequest

from apps.pkg.logger.logger import new_logger
from apps.utils.otp import generate_otp_code
from apps.authentication.exceptions import UserNotFound, IpBlocked, AuthFieldNotAllowedToReceiveSms
from apps.common.logger import properties_with_user
from apps.pkg.logger import category
from apps.pkg.logger.base import Log
from apps.pkg.sms.sms import get_sms_service
from apps.pkg.token.token import generate_refresh_token_with_claims, generate_access_token_with_claims
from apps.utils import client
from apps.authentication.services.token import encrypt_token, get_refresh_token_claims, get_access_token_claims
from apps.utils.cache import get_cache, set_cache, incr_cache

User = get_user_model()
log = new_logger()

LOGIN_SUF_KEY = "login"


def login_by_password(request: HttpRequest, username: str, password: str) -> Dict:
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist as err:
        raise ValueError(err)

    if not user.check_password(password):
        raise ValueError("user does not exist")

    client_info = client.get_client_info(request=request)

    refresh_token = generate_refresh_token_with_claims(
        claims=get_refresh_token_claims(**client_info, user_id=user.id), encrypt_func=encrypt_token)

    access_token = generate_access_token_with_claims(
        claims=get_access_token_claims(**client_info, **user.__dict__),
        encrypt_func=encrypt_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def check_ip_address_access(ip_address: str) -> bool:
    key = ip_address + "count"
    count = get_cache(key=key)
    if not count:
        set_cache(key=key, value=1, timeout=86400)
        return True

    if count <= 10:
        incr_cache(key=key)
        return True

    return False


def check_auth_field_allow_to_receive_sms(auth_field, client_info):
    if get_cache(key=auth_field+LOGIN_SUF_KEY):
        log.error(message="You can only receive a code every two minutes",
                  category=category.LOGIN, sub_category=category.LOGIN_BY_PHONE_NUMBER,
                  properties={**client_info, "AuthField": auth_field})
        raise AuthFieldNotAllowedToReceiveSms


def login_by_phone_number(request: HttpRequest, phone_number: str) -> None:
    client_info = client.get_client_info(request=request)

    check_auth_field_allow_to_receive_sms(auth_field=phone_number, client_info=client_info)

    if not check_ip_address_access(ip_address=client_info[client.IP_ADDRESS]):
        log.error(message="This IP address has been blocked",
                  category=category.LOGIN, sub_category=category.LOGIN_BY_PHONE_NUMBER, properties=client_info)
        raise IpBlocked

    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist as err:
        log.error(message=f"user with phone number {phone_number} not found",
                  category=category.LOGIN, sub_category=category.LOGIN_BY_PHONE_NUMBER,
                  properties={**client_info, "PhoneNumber": phone_number})
        raise UserNotFound

    code = generate_otp_code()
    properties = properties_with_user(user=user, extra=client_info)
    log.info(message=f"Send the code to the {user.username} user to login", category=category.LOGIN,
             sub_category=category.LOGIN_BY_PHONE_NUMBER, properties=properties)
    set_cache(key=phone_number+LOGIN_SUF_KEY, value=code, timeout=120)

    sms = get_sms_service()
    sms.send(code)


def verify_phone_number(request: HttpRequest, phone_number: str, code: str) -> Dict:
    pass


def register_user(request: HttpRequest, username: str, email: str, password: str) -> Dict:
    user = User.objects.create_user(username=username, email=email, password=password)

    client_info = client.get_client_info(request=request)

    refresh_token = generate_refresh_token_with_claims(
        claims=get_refresh_token_claims(**client_info, user_id=user.id), encrypt_func=encrypt_token)

    access_token = generate_access_token_with_claims(
        claims=get_access_token_claims(**client_info, **user.__dict__),
        encrypt_func=encrypt_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

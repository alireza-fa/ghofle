from typing import Dict

from django.contrib.auth import get_user_model
from django.http import HttpRequest

from apps.pkg.logger.logger import new_logger
from apps.utils.otp import generate_otp_code
from apps.authentication.exceptions import UserNotFound, IpBlocked, AuthFieldNotAllowedToReceiveSms, \
    InvalidCode
from apps.common.logger import properties_with_user
from apps.pkg.logger import category
from apps.pkg.sms.sms import get_sms_service
from apps.pkg.token.token import generate_refresh_token_with_claims, generate_access_token_with_claims
from apps.utils import client
from apps.authentication.services.token import encrypt_token, get_refresh_token_claims, get_access_token_claims, \
    generate_token
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

    return generate_token(client_info=client_info, user=user)


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
                  category=category.AUTH, sub_category=category.LOGIN_BY_PHONE_NUMBER,
                  properties={**client_info, "AuthField": auth_field})
        raise AuthFieldNotAllowedToReceiveSms


def login_by_phone_number(request: HttpRequest, phone_number: str) -> None:
    client_info = client.get_client_info(request=request)

    check_auth_field_allow_to_receive_sms(auth_field=phone_number, client_info=client_info)

    if not check_ip_address_access(ip_address=client_info[client.IP_ADDRESS]):
        log.error(message="This IP address has been blocked",
                  category=category.AUTH, sub_category=category.LOGIN_BY_PHONE_NUMBER, properties=client_info)
        raise IpBlocked

    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        log.error(message=f"user with phone number {phone_number} not found",
                  category=category.AUTH, sub_category=category.LOGIN_BY_PHONE_NUMBER,
                  properties={**client_info, "PhoneNumber": phone_number})
        raise UserNotFound

    code = generate_otp_code()
    properties = properties_with_user(user=user, extra=client_info)
    properties["code"] = code
    log.info(message=f"Send the code to the {user.username} user to login", category=category.AUTH,
             sub_category=category.LOGIN_BY_PHONE_NUMBER, properties=properties)
    set_cache(key=phone_number+LOGIN_SUF_KEY, value={"code": code, "phone_number": phone_number, "state": "login"},
              timeout=120)

    sms = get_sms_service()
    sms.send(code)


def check_validate_auth_field_for_verify(auth_field: str, client_info: Dict):
    key = auth_field + "count"
    count = get_cache(key=key)

    if not count:
        set_cache(key=key, value=1, timeout=120)
        count = 1

    if count <= 5:
        incr_cache(key=key)
        return None

    log.error(message="auth filed not validate for verification", category=category.AUTH,
              sub_category=category.VERIFY_LOGIN, properties={**client_info, "AuthField":auth_field})
    raise InvalidCode


def login_state(client_info: Dict, cache_info: Dict, phone_number: str) -> Dict:
    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        log.error(message=f"user with phone number {phone_number} not found",
                  category=category.AUTH, sub_category=category.LOGIN_BY_PHONE_NUMBER,
                  properties={**client_info, "PhoneNumber": phone_number})
        raise UserNotFound

    return generate_token(client_info=client_info, user=user)


def verify_sign_user(request: HttpRequest, phone_number: str, code: str) -> Dict:
    client_info = client.get_client_info(request=request)
    check_validate_auth_field_for_verify(auth_field=phone_number, client_info=client_info)

    cache_info = get_cache(key=phone_number+LOGIN_SUF_KEY)
    if cache_info["code"] != code:
        log.error(message="invalid code", category=category.AUTH, sub_category=category.VERIFY_LOGIN,
                  properties={**client_info, "PhoneNumber": phone_number})
        raise InvalidCode

    if cache_info["state"] == "login":
        return login_state(client_info=client_info, cache_info=cache_info, phone_number=phone_number)


def register_user(request: HttpRequest, username: str, email: str, password: str) -> Dict:
    user = User.objects.create_user(username=username, email=email, password=password)

    client_info = client.get_client_info(request=request)

    return generate_token(client_info=client_info, user=user)

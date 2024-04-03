from typing import Dict

from django.contrib.auth import get_user_model
from django.http import HttpRequest

from apps.accounts.selectors.base_user import get_user_by_phone_number, get_user_by_username
from apps.accounts.services.base_user import create_base_user
from pkg.logger.logger import new_logger
from apps.utils.otp import generate_otp_code
from apps.authentication.exceptions import IpBlocked, AuthFieldNotAllowedToReceiveSms, InvalidCode
from apps.common.logger import properties_with_user
from pkg.logger import category
from pkg.sms.sms import get_sms_service
from apps.utils import client
from apps.authentication.v1.services.token import generate_token
from apps.utils.cache import get_cache, set_cache, incr_cache, delete_cache

User = get_user_model()
log = new_logger()

SIGN_SUF_KEY = "sign"


def login_by_password(request: HttpRequest, username: str, password: str) -> Dict:
    user = get_user_by_username(username=username)

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
    if get_cache(key=auth_field+SIGN_SUF_KEY):
        log.error(message="You can only receive a code every two minutes",
                  category=category.AUTH, sub_category=category.SIGN_USER,
                  properties={**client_info, "AuthField": auth_field})
        raise AuthFieldNotAllowedToReceiveSms


def login_by_phone_number(request: HttpRequest, phone_number: str) -> None:
    client_info = client.get_client_info(request=request)

    check_auth_field_allow_to_receive_sms(auth_field=phone_number, client_info=client_info)

    if not check_ip_address_access(ip_address=client_info[client.IP_ADDRESS]):
        log.error(message="This IP address has been blocked",
                  category=category.AUTH, sub_category=category.LOGIN_BY_PHONE_NUMBER, properties=client_info)
        raise IpBlocked

    user = get_user_by_phone_number(phone_number=phone_number)

    code = generate_otp_code()

    properties = properties_with_user(user=user, extra=client_info)
    properties["code"] = code
    log.info(message=f"Send the code to the {user.username} user to login", category=category.AUTH,
             sub_category=category.LOGIN_BY_PHONE_NUMBER, properties=properties)

    set_cache(key=phone_number+SIGN_SUF_KEY, value={"code": code, "phone_number": phone_number, "state": "login"},
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


def login_state(client_info: Dict, phone_number: str) -> Dict:
    user = get_user_by_phone_number(phone_number=phone_number)

    return generate_token(client_info=client_info, user=user)


def register_state(client_info: Dict, username: str, phone_number: str, password: str) -> Dict:
    user = create_base_user(username=username, phone_number=phone_number, password=password)

    return generate_token(client_info=client_info, user=user)


def verify_sign_user(request: HttpRequest, phone_number: str, code: str) -> Dict:
    client_info = client.get_client_info(request=request)
    check_validate_auth_field_for_verify(auth_field=phone_number, client_info=client_info)
    properties = {**client_info, "PhoneNumber": phone_number}

    cache_info = get_cache(key=phone_number+SIGN_SUF_KEY)
    if not cache_info:
        raise InvalidCode

    if cache_info["code"] != code:
        log.error(message="invalid code", category=category.AUTH, sub_category=category.SIGN_USER,
                  properties=properties)
        raise InvalidCode

    if cache_info["state"] == "login":
        delete_cache(key=phone_number+SIGN_SUF_KEY)
        log.info(message=f"user {phone_number} logged in",
                 category=category.AUTH, sub_category=category.VERIFY_LOGIN,
                 properties=properties)
        return login_state(client_info=client_info, phone_number=phone_number)

    delete_cache(key=phone_number+SIGN_SUF_KEY)
    log.info(message=f"user {phone_number} registered",
             category=category.AUTH, sub_category=category.REGISTER_USER,
             properties=properties)
    return register_state(client_info=client_info, username=cache_info["username"],
                          phone_number=cache_info["phone_number"], password=cache_info["password"])


def register_user(request: HttpRequest, username: str, phone_number: str, password: str | None = None) -> None:
    client_info = client.get_client_info(request=request)
    check_auth_field_allow_to_receive_sms(auth_field=phone_number, client_info=client_info)

    if not check_ip_address_access(ip_address=client_info[client.IP_ADDRESS]):
        log.error(message="This IP address has been blocked",
                  category=category.AUTH, sub_category=category.REGISTER_USER, properties=client_info)
        raise IpBlocked

    code = generate_otp_code()

    properties = {**client_info, "PhoneNumber": phone_number, "Code": code}
    log.info(message=f"Send the code to the {phone_number} user to login", category=category.AUTH,
             sub_category=category.LOGIN_BY_PHONE_NUMBER, properties=properties)

    set_cache(
        key=phone_number+SIGN_SUF_KEY,
        value={"code": code, "phone_number": phone_number, "username": username,
               "password": password, "state": "register"}, timeout=120)

    sms = get_sms_service()
    sms.send(code)

from typing import Dict

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from d_jwt_auth.token import generate_token

from apps.accounts.v1.selectors.base_user import get_user_by_phone_number, create_new_user
from apps.api import response_code
from apps.utils.randomly import generate_number_code_str
from pkg.logger.logger import new_logger
from apps.common.logger import get_default_log_properties, get_default_log_properties_with_user
from pkg.logger import category
from pkg.redis.redis import get_redis_connection
from pkg.richerror.error import RichError, get_error_info, error_message
from pkg.sms.sms import get_sms_service
from apps.utils import client


User = get_user_model()
logger = new_logger()
redis = get_redis_connection()
sms = get_sms_service()

SIGN_SUF_KEY = "sign"
IP_ADDRESS_TRY_SIGN_COUNT_PER_DAY = 10
OTP_LENGTH = 6
OTP_CODE_TRYING_CHANCE = 5


def check_ip_address_access(ip_address: str) -> None:
    op = "authentication.services.sign_user.check_ip_address_access"

    key = "%s:%s" % (ip_address, SIGN_SUF_KEY)
    count = redis.get(key=key)

    if not count:
        redis.incr(key=key, timeout=86400)
        return

    if count <= IP_ADDRESS_TRY_SIGN_COUNT_PER_DAY:
        redis.incr(key=key, timeout=86400)
        return

    raise RichError(operation=op, message="Ip address blocked, ip address is: %s" % ip_address,
                    code=response_code.IP_BLOCKED)


def get_auth_field_redis_key(auth_field: str) -> str:
    return "%s:%s" % (auth_field, SIGN_SUF_KEY)


def check_auth_field_allow_to_receive_sms(auth_field):
    if redis.get(key=get_auth_field_redis_key(auth_field=auth_field)):
        raise RichError(
            operation="authentication.services.check_auth_field_allow_to_receive_sms",
            message="You can only receive a code once every two minutes, auth field is %s" % auth_field,
            code=response_code.USER_NOT_ALLOW_TO_RECEIVE_SMS,
        )


def login_by_phone_number(request: HttpRequest, phone_number: str) -> None:
    client_info = client.get_client_info(request=request)
    code = generate_number_code_str(num_digits=OTP_LENGTH)
    properties = get_default_log_properties(client_info=client_info, code=code, phone_number=phone_number)

    try:
        check_auth_field_allow_to_receive_sms(auth_field=phone_number)

        user = get_user_by_phone_number(phone_number=phone_number)

        check_ip_address_access(ip_address=client_info[client.IP_ADDRESS])

        redis.set(
            key=get_auth_field_redis_key(auth_field=phone_number),
            value={"code": code, "phone_number": user.phone_number, "state": "login"}, timeout=120)

        logger.info(message="Sent a code for login user by phone number",
                    category=category.LOGIN, sub_category=category.LOGIN_BY_PHONE_NUMBER, properties=properties)

        sms.send(code)
    except Exception as ex:
        properties[category.ERROR] = get_error_info(error=ex)
        logger.error(message=error_message(error=ex),
                     category=category.LOGIN, sub_category=category.LOGIN_BY_PHONE_NUMBER, properties=properties)
        raise ex


def register_user(request: HttpRequest, **kwargs) -> None:
    client_info = client.get_client_info(request=request)
    properties = get_default_log_properties(client_info=client.get_client_info(request=request), **kwargs)
    code = generate_number_code_str(num_digits=OTP_LENGTH)

    try:
        check_auth_field_allow_to_receive_sms(auth_field=kwargs["phone_number"])

        check_ip_address_access(ip_address=client_info[client.IP_ADDRESS])

        redis.set(
            key=get_auth_field_redis_key(auth_field=kwargs["phone_number"]),
            value={"code": code, **kwargs, "state": "register"},
            timeout=120)

        sms.send(code)

        logger.info(message="sent a code for register user by phone number",
                    category=category.REGISTER_USER, sub_category=category.REGISTER_BY_PHONE_NUMBER, properties=properties)

    except Exception as ex:
        properties[category.ERROR] = get_error_info(error=ex)
        logger.error(message=error_message(error=ex),
                     category=category.REGISTER_USER, sub_category=category.REGISTER_BY_PHONE_NUMBER, properties=properties)
        raise ex


def validate_user_for_trying_verifying(auth_field: str) -> None:
    op = "authentication.services.sign_user.validate_user_for_trying_verifying"

    key = "%s:try_verify:count" % auth_field
    count = redis.get(key=key)

    if not count:
        redis.incr(key=key, timeout=120)
        count = 1

    if count <= OTP_CODE_TRYING_CHANCE:
        redis.incr(key=key, timeout=120)
        return None

    raise RichError(
        operation=op,
        message="You have tried more than five times and your code is considered invalid. auth_field: %s" % auth_field,
        code=response_code.INVALID_CODE
    )


def get_user_info_for_verifying_from_cache(auth_field: str) -> Dict:
    op = "authentication.services.sign_user.get_user_info_for_verifying_from_cache"

    cache_info = redis.get(key=get_auth_field_redis_key(auth_field=auth_field))
    if not cache_info:
        raise RichError(
            operation=op,
            message="We did not find the user information in the cache. Probably more than two minutes"
                    " have passed and it has been deleted.",
            code=response_code.INVALID_CODE,
        )

    return cache_info


def validate_code_match(correct_code, request_code) -> None:
    op = "authentication.services.sign_user.validate_code_match"

    if correct_code != request_code:
        raise RichError(operation=op, message="The codes are not the same.", code=response_code.INVALID_CODE)


def signing_user_by_cache_info_with_phone(request: HttpRequest, cache_info: Dict) -> User:
    client_info = client.get_client_info(request=request)

    if cache_info["state"] == "login":
        user = get_user_by_phone_number(phone_number=cache_info["phone_number"])
        properties = get_default_log_properties_with_user(client_info=client_info, user=user)
        logger.info(message="get user for signing by phone",
                    category=category.VERIFY_SIGN, sub_category=category.VERIFY_SIGN_USER_BY_OTP_CODE, properties=properties)

    else:
        user = create_new_user(username=cache_info["username"], phone_number=cache_info["phone_number"])
        properties = get_default_log_properties_with_user(client_info=client_info, user=user)
        logger.info(message="create a user for sign up",
                    category=category.VERIFY_SIGN, sub_category=category.VERIFY_SIGN_USER_BY_OTP_CODE, properties=properties)

    redis.delete(get_auth_field_redis_key(auth_field=cache_info["phone_number"]))
    return user


def verify_sign_user_by_code(request: HttpRequest, auth_field: str, code: str) -> Dict:
    validate_user_for_trying_verifying(auth_field=auth_field)
    client_info = client.get_client_info(request=request)
    properties = get_default_log_properties(client_info=client_info, auth_field=auth_field, code=code)

    try:
        cache_info = get_user_info_for_verifying_from_cache(auth_field=auth_field)

        validate_code_match(correct_code=cache_info["code"], request_code=code)

        user = signing_user_by_cache_info_with_phone(request=request, cache_info=cache_info)

        logger.info(message="generate access and refresh token for user",
                    category=category.VERIFY_SIGN, sub_category=category.VERIFY_SIGN_USER_BY_OTP_CODE, properties=properties)

        return generate_token(request=request, user=user,
                              roles=list(user.roles.all().values_list("role", flat=True)),
                              avatar_image_filename=None if not user.avatar_image else user.avatar_image.filename)
    except Exception as ex:
        properties[category.ERROR] = get_error_info(error=ex)
        logger.error(message=error_message(error=ex),
                     category=category.VERIFY_SIGN, sub_category=category.VERIFY_SIGN_USER_BY_OTP_CODE, properties=properties)
        raise ex

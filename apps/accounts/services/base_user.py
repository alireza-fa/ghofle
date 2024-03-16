from random import randint
from typing import Dict
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone

from apps.accounts.models import Role, UserRole
from apps.accounts.tasks import delete_object_task
from apps.authentication.token import invalidating_access_token
from apps.common.tasks import send_mail_task
from apps.pkg.email_service.base import Mail
from apps.pkg.logger.logger import new_logger
from apps.utils import constants
from apps.pkg.logger.base import Log
from apps.pkg.logger import category
from apps.utils.auth import get_token_from_header
from apps.utils.file import change_filename
from apps.utils.log import get_properties, convert_user_to_map
from apps.utils.otp import check_number_allow_to_receive_sms
from apps.utils.cache import set_cache, get_cache, delete_cache
from apps.api.response_code import INVALID_OTP, ERROR_TRANSLATION, PHONE_NUMBER_EXIST

User = get_user_model()


def get_client_info(request: HttpRequest) -> Dict:
    ip_address = request.META.get('REMOTE_ADDR')

    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip_address = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]

    return {
        "device_name": request.META.get('HTTP_USER_AGENT', ''),
        "ip_address": ip_address
    }


def generate_otp_code() -> str:
    return str(randint(a=100000, b=999999))


def set_update_phone_number_cache(user_id: int, phone_number: str, new_phone_number, client_info: Dict, code: str) -> None:
    key = client_info["ip_address"] + code
    value = {"user_id": user_id, "new_phone_number": new_phone_number}

    set_cache(key=phone_number, value=1, timeout=120)
    set_cache(key=client_info["ip_address"], value=1, timeout=120)
    set_cache(key=new_phone_number, value=1, timeout=120)

    set_cache(key=key, value=value, timeout=120)


@transaction.atomic
def create_user(*, fullname, national_code, phone_number,
                email, is_active=True, is_admin=False, password=None, created_by=-1) -> User:
    user = User(
        fullname=fullname,
        national_code=national_code,
        phone_number=phone_number,
        email=email,
        is_active=is_active,
        is_admin=is_admin,
        created_by=created_by,
    )

    if password is not None:
        user.set_password(password)
    else:
        user.set_unusable_password()

    user.full_clean()
    user.save()

    default_role = Role.objects.get(name=constants.DEFAULT_ROLE)

    if is_admin:
        admin_role = Role.objects.get(name=constants.ADMIN_ROLE)
        UserRole.objects.create(user=user, role=default_role)
        UserRole.objects.create(user=user, role=admin_role)
    else:
        UserRole.objects.create(user=user, role=default_role)

    return user


def check_phone_number_exist(phone_number: str) -> bool:
    users = User.objects.filteinvalidating_access_tokenr(phone_number=phone_number)
    return users.exists()


def user_change_phone_number(log: Log, request: HttpRequest, new_phone_number) -> None:
    client_info = get_client_info(request=request)
    properties = get_properties(client_info=client_info)
    properties[category.PHONE_NUMBER] = request.user.phone_number
    properties["NewPhoneNumber"] = new_phone_number

    check = check_number_allow_to_receive_sms(request.user.phone_number, client_info["ip_address"])
    if not check:
        log.error(
            message=f"phone number {request.user.phone_number} not allow to receive sms",
            category=category.PROFILE, sub_category=category.UPDATE_PROFILE_PHONE_NUMBER, properties=properties
        )
        raise PermissionError("not allow to receive sms")
    check = check_number_allow_to_receive_sms(new_phone_number, client_info["ip_address"])
    if not check:
        log.error(
            message=f"new phone number {new_phone_number} not allow to receive sms",
            category=category.PROFILE, sub_category=category.UPDATE_PROFILE_PHONE_NUMBER, properties=properties
        )
        raise PermissionError("not allow to receive sms")

    code = generate_otp_code()

    properties[category.CODE] = code

    set_update_phone_number_cache(
        user_id=request.user.id,
        phone_number=request.user.phone_number,
        new_phone_number=new_phone_number,
        client_info=client_info,
        code=code)

    # TODO: Send code for user phone number

    log.info(
        message=f"send a code for user {request.user.phone_number} due to change phone number",
        category=category.PROFILE, sub_category=category.UPDATE_PROFILE_PHONE_NUMBER, properties=properties
    )


def user_change_phone_number_verify(log: Log, request: HttpRequest, code: str):
    client_info = get_client_info(request=request)
    properties = get_properties(client_info=client_info)
    properties[category.CODE] = code

    key = client_info["ip_address"] + code

    cache_info = get_cache(key=key)
    if not cache_info:
        log.error(
            message=f"cannot find cache info for key {key}",
            category=category.PROFILE, sub_category=category.UPDATE_PROFILE_PHONE_NUMBER_VERIFY, properties=properties
        )
        raise ValueError(ERROR_TRANSLATION[INVALID_OTP])

    if check_phone_number_exist(cache_info["new_phone_number"]):
        log.error(
            message=ERROR_TRANSLATION[PHONE_NUMBER_EXIST],
            category=category.PROFILE, sub_category=category.UPDATE_PROFILE_PHONE_NUMBER_VERIFY, properties=properties
        )
        raise ValueError(ERROR_TRANSLATION[PHONE_NUMBER_EXIST])

    user = User.objects.get(id=request.user.id)
    user.phone_number = cache_info["new_phone_number"]
    user.save()

    invalidating_access_token(token=get_token_from_header(headers=request.headers))

    delete_cache(key)


def update_email(log: Log, request: HttpRequest, new_email: str) -> None:
    user = User.objects.get(id=request.user.id)
    properties = {
        **get_properties(get_client_info(request=request)),
        **convert_user_to_map(user=user)
    }

    if not user.email == new_email:
        user.email = new_email
        user.verified_email = False
        user.save()

        log.info(message=f"{user.fullname} email was updated", category=category.PROFILE,
                 sub_category=category.UPDATE_PROFILE_EMAIL, properties=properties)
        return

    log.info(message=f"{user.fullname} email was updated, but the new email is the same as the old email",
             category=category.PROFILE, sub_category=category.UPDATE_PROFILE_EMAIL, properties=properties)


def email_confirm(log: Log, request: HttpRequest) -> None:
    if get_cache(key=request.user.email + "confirm"):
        log.error(message="please try again two minutes later",
                  category=category.PROFILE, sub_category=category.EMAIL_CONFIRM,
                  properties=get_client_info(request=request))
        raise PermissionError

    user = User.objects.get(id=request.user.id)

    properties = {
        **get_client_info(request=request),
        **convert_user_to_map(user=user)
    }

    if user.email is None:
        log.error(message="user email does not exist",
                  category=category.PROFILE, sub_category=category.EMAIL_CONFIRM, properties=properties)
        raise ValueError

    key = user.email + "confirm"
    code = generate_otp_code()
    set_cache(key=key, value={"code": code}, timeout=120)

    properties[category.CODE] = code
    log.info(message=f"sending email to {user.email} for confirm email",
             category=category.PROFILE, sub_category=category.EMAIL_CONFIRM, properties=properties)

    send_mail_task.delay(user.email, "verify email", code)


def email_verify(log: Log, request: HttpRequest, code: str) -> None:
    properties = {
        **get_client_info(request=request),
        **convert_user_to_map(user=request.user),
        category.CODE: code
    }

    cache_info = get_cache(key=request.user.email + "confirm")
    if not cache_info:
        log.error(message=f"cannot find user cache",
                  category=category.PROFILE, sub_category=category.EMAIL_VERIFY, properties=properties)
        raise ValueError

    properties["CurrentCode"] = cache_info["code"]

    if code != cache_info["code"]:
        log.error(message=f"don't match codes, email: {request.user.email}",
                  category=category.PROFILE, sub_category=category.EMAIL_VERIFY, properties=properties)
        raise ValueError

    user = User.objects.get(id=request.user.id)
    user.verified_email = True
    user.save()
    log.error(message=f"email verified, email: {user.email}",
              category=category.PROFILE, sub_category=category.EMAIL_VERIFY, properties=properties)


def update_image(log: Log, request: HttpRequest, file: bytes) -> None:
    client_info = get_client_info(request=request)

    user = User.objects.get(id=request.user.id)

    properties = {
        **get_properties(client_info=client_info),
        **convert_user_to_map(user=user),
    }

    if user.avatar_image:
        delete_object_task.delay(user.avatar_image.name)
        log.info(message=f"file with filename {file.name} deleted",
                 category=category.PROFILE, sub_category=category.UPDATE_PROFILE_IMAGE, properties=properties)

    file.name = change_filename(filename=file.name)

    try:
        user.avatar_image = file
        user.last_image_update = timezone.now()
        user.save()
    except TimeoutError:
        raise TimeoutError("error while uploading avatar image")

    log.info(message=f"file with filename: {file.name} uploaded",
                     category=category.PROFILE, sub_category=category.UPDATE_PROFILE_IMAGE, properties=properties)

from datetime import timedelta
from typing import Dict

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.utils import timezone

from apps.common.storage import put_file
from apps.files.exceptions import RichPadlockLimit, PadlockDoesNotExist, AccessDeniedPadlockFile, AlreadyPadlockBuyErr
from apps.files.models import Padlock, File, PadLockUser
from apps.finance.models import Gateway, Payment
from apps.finance.services.payment import create_payment, get_payment_request
from apps.pkg.logger import category
from apps.pkg.logger.logger import new_logger
from apps.common.logger import properties_with_user
from apps.pkg.storage.storage import get_storage
from apps.utils import client
from apps.files.v1.selectors.padlock import get_padlock

log = new_logger()
User = get_user_model()
storage = get_storage()


def create_file(*, file: object, extra: Dict) -> File:
    f = put_file(file=file, log_properties=extra)
    file = File()
    file.filename = f["filename"]
    file.size = f["size"]
    file.expire_at = timezone.now() + timedelta(days=30)
    file.save()
    return file


def create_padlock(*, request: HttpRequest, title: str, description: str, price: int, file: object,
                   thumbnail: object | None = None, review_active: bool = True) -> Padlock:
    user = request.user
    client_info = client.get_client_info(request=request)

    if Padlock.objects.filter(owner=user, checked=False).count() >= 5:
        raise RichPadlockLimit

    properties = {
        **properties_with_user(user=user, extra=client_info)
    }

    padlock = Padlock.objects.create(owner=user, title=title, description=description,
                                     review_active=review_active, price=price)

    if thumbnail:
        f = create_file(file=thumbnail, extra=properties)
        padlock.thumbnail = f

    f = create_file(file=file, extra=properties)
    padlock.file = f

    padlock.save()
    log.info(message=f"create a new padlock for user {user.username}",
              category=category.PADLOCK, sub_category=category.CREATE_PADLOCK, properties=properties)
    return padlock


def delete_padlock(*, request: HttpRequest, padlock_id) -> None:
    user = request.user

    try:
        padlock = Padlock.objects.get(owner=user, id=padlock_id, is_deleted=False)
    except Padlock.DoesNotExist:
        raise PadlockDoesNotExist

    padlock.is_deleted = True
    padlock.save()


def open_padlock_file(request: HttpRequest, padlock_id: int):
    user = request.user
    properties = properties_with_user(user=user, extra=client.get_client_info(request=request))

    try:
        padlock_user = PadLockUser.objects.get(user__id=user.id, padlock__id=padlock_id, padlock__is_active=True)
    except PadLockUser.DoesNotExist:
        log.error(message=f"PadlockUser with id: {padlock_id} does not exist",
                  category=category.POSTGRESQL, sub_category=category.SELECT, properties=properties)
        raise PadlockDoesNotExist

    if padlock_user.use_time >= 3:
        raise AccessDeniedPadlockFile

    padlock_user.use_time += 1
    log.info(message=f"user {user.username} open padlock {padlock_id} file",
             category=category.PADLOCK, sub_category=category.OPEN_PADLOCK_FILE, properties=properties)
    padlock_user.save()

    return storage.get_file_url(filename=padlock_user.padlock.file.filename)


def padlock_buy(request: HttpRequest, padlock_id: int) -> str:
    padlock = get_padlock(padlock_id=padlock_id)
    user = request.user

    padlock_users = PadLockUser.objects.filter(padlock=padlock, user=user)
    if not padlock_users.exists():
        padlock_user = PadLockUser(padlock=padlock, user=user)
    else:
        padlock_user = padlock_users.first()
        if padlock_user.payment.status:
            raise AlreadyPadlockBuyErr
        padlock_user.payment.delete()

    payment = create_payment(gateway_name=Gateway.ZIBAL, user=user, payment_type=Payment.PADLOCK,
                             amount=padlock.price * 10, description=f"pay for {padlock.title}")

    request_pay = get_payment_request(payment=payment)

    payment.track_id = request_pay["trackId"]
    payment.save()

    padlock_user.payment = payment
    padlock_user.save()

    return request_pay["link"]

from datetime import datetime, timedelta

from d_jwt_auth.models import UserAuth
from d_jwt_auth.services import update_user_auth_uuid
from django.db import transaction
from django.http import HttpRequest

from apps.accounts.v1.selectors.base_user import get_user_by_id
from apps.api import response_code
from apps.common.logger import get_default_log_properties_with_user
from apps.common.models import File
from apps.common.services.file import create_file
from apps.common.services.storage import get_file_url
from apps.utils import client
from pkg.logger import category
from pkg.logger.logger import new_logger
from pkg.redis.redis import get_redis_connection
from pkg.richerror.error import RichError, get_error_info

logger = new_logger()
redis = get_redis_connection()
CHANGE_AVATAR_IMAGE_PER: timedelta = timedelta(hours=1)


def user_allow_to_change_avatar_image(user_id: int) -> None:
    op = "accounts.services.profile.user_allow_to_change_avatar_image"
    key = "user:%d:last_avatar_image_time"
    value = redis.get(key=key)

    if value:
        raise RichError(
            operation=op,
            message="The request to change user %d profile picture has exceeded the limit" % user_id,
            code=response_code.TOO_MANY_REQUEST_CHANGE_IMAGE
        )

    redis.set(key=key, value=1, timeout=(datetime.now() + CHANGE_AVATAR_IMAGE_PER).second)


def update_profile_avatar_image(request: HttpRequest, avatar_image: bytearray) -> str:
    user = get_user_by_id(user_id=request.user.id)
    properties = get_default_log_properties_with_user(client_info=client.get_client_info(request=request), user=user)

    try:
        user_allow_to_change_avatar_image(user_id=user.id)

        with transaction.atomic():
            file = create_file(file_type=File.IMAGE, file=avatar_image)

            user.avatar_image = file
            user.save()

            update_user_auth_uuid(user_id=user.id, token_type=UserAuth.ACCESS_TOKEN)

        logger.info(message="user %d uploaded a new avatar image" % user.id,
                    category=category.PROFILE, sub_category=category.UPDATE_AVATAR_IMAGE, properties=properties)

        return get_file_url(filename=file.filename, log_properties=properties)

    except Exception as ex:
        properties[category.ERROR] = get_error_info(error=ex)
        logger.error(message=str(ex),
                     category=category.PROFILE, sub_category=category.UPDATE_AVATAR_IMAGE, properties=properties)
        raise ex

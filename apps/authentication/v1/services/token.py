from d_jwt_auth.models import UserAuth
from d_jwt_auth.services import update_user_auth_uuid
from d_jwt_auth.token import get_token_claims_info, refresh_access_token, verify_token
from d_jwt_auth.constants import USER_ID
from django.http import HttpRequest

from apps.accounts.v1.selectors.base_user import get_user_by_id
from apps.api import response_code
from apps.common.logger import get_default_log_properties, get_default_log_properties_with_user
from apps.utils import client
from pkg.logger import category
from pkg.logger.logger import new_logger
from pkg.richerror.error import get_error_info, RichError

logger = new_logger()


def token_refresh(request: HttpRequest, raw_refresh_token: str) -> str:
    op = "authentication.services.token.token_refresh"

    client_info = client.get_client_info(request=request)
    properties = get_default_log_properties(client_info=client_info)

    try:
        refresh_claims = get_token_claims_info(request=request, raw_token=raw_refresh_token)
        user = get_user_by_id(user_id=refresh_claims[USER_ID])
        properties = get_default_log_properties_with_user(client_info=client_info, user=user)
        access_token = refresh_access_token(
            request=request,
            raw_refresh_token=raw_refresh_token,
            roles=list(user.roles.all().values_list("role", flat=True)),
            avatar_image_filename=None if not user.avatar_image else user.avatar_image.filename
        )
        logger.info("refresh access token",
                    category=category.TOKEN, sub_category=category.REFRESH_ACCESS_TOKEN, properties=properties)

        return access_token

    except Exception as ex:
        properties[category.ERROR] = get_error_info(error=ex)
        logger.error(message=str(ex),
                     category=category.LOGIN, sub_category=category.LOGIN_BY_PHONE_NUMBER, properties=properties)
        raise RichError(operation=op, code=response_code.INVALID_TOKEN, error=ex)


def token_verify(request: HttpRequest, raw_token: str) -> bool:
    return verify_token(request=request, raw_token=raw_token)


def token_ban(request: HttpRequest) -> None:
    client_info = client.get_client_info(request=request)
    properties = get_default_log_properties_with_user(client_info=client_info, user=request.user)

    update_user_auth_uuid(user_id=request.user.id, token_type=UserAuth.REFRESH_TOKEN)
    update_user_auth_uuid(user_id=request.user.id, token_type=UserAuth.ACCESS_TOKEN)

    logger.info(message="banned user tokens",
                category=category.TOKEN, sub_category=category.BAN_TOKEN, properties=properties)

from typing import Dict

from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.status import HTTP_400_BAD_REQUEST

from apps.api.error_translate import get_code
from apps.api.response_code import ERROR_TRANSLATION, BAD_REQUEST


def base_response(*, status_code: int, code: int, result: Dict | None = None) -> Response:
    return Response(data={"result": result, "code": code}, status=status_code)


def base_response_with_error(*, err: Exception, status_code: int | None = None,
                             code: int | None = None, error: str | None = None) -> Response:
    code = get_code(error=err)
    return Response(data={"code": code, "error": ERROR_TRANSLATION[code]}, status=code // 100)


def base_response_with_validation_error(*, error: ValidationError) -> Response:
    return Response(data={"code": BAD_REQUEST, "error": error}, status=HTTP_400_BAD_REQUEST)

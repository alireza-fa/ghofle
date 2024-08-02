from apps.api import response_code
from pkg.richerror.error import RichError, error_code


def get_code(error: Exception):
    if isinstance(error, RichError):
        return error_code(error=error)

    return response_code.INTERNAL_SERVER_ERROR

from typing import Optional, List

from . import constants
from . import codes


class RichError(Exception):

    def __init__(self, operation: str, message: str = "", code: int = codes.UNKNOWN_CODE,
                 error: Optional[Exception] = None) -> None:
        self._operation = operation
        self._message = message
        self._code = code
        self._error = error

    def __str__(self) -> str:
        return self._message if self._message or not self._error else str(self._error)


def error_code(error: Exception) -> int:
    while isinstance(error, RichError) and error._code == codes.UNKNOWN_CODE and error._error:
        error = error._error

    return codes.UNKNOWN_CODE if not isinstance(error, RichError) else error._code


def _error_info(error: Exception):
    if isinstance(error, RichError):
        return {
            constants.Operation: error._operation,
            constants.Code: error_code(error),
            constants.Message: str(error)
        }

    return {
        constants.Operation: "",
        constants.Code: codes.UNKNOWN_CODE,
        constants.Message: str(error)
    }


def get_error_recursive(error: Exception, errors: List) -> List:
    errors.append(_error_info(error))
    if isinstance(error, RichError) and error._error:
        return get_error_recursive(error._error, errors)

    return errors


def get_error_info(error: Exception) -> List:
    return get_error_recursive(error=error, errors=[])

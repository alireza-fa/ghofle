from typing import Optional, Dict, List

from . import constants
from . import codes


class RichError(Exception):
    _operation: str
    _message: Optional[str] = None
    _code: Optional[int] = None
    _error: Optional[str] = None

    def __init__(self, operation: str, message: str = "", code: int = codes.UNKNOWN_CODE,
                 error: Exception | None = None) -> None:
        self._operation = operation
        self._message = message
        self._code = code
        self._error = error

    def __str__(self) -> str:
        return error_message(self)


def error_message(error: Exception) -> str:
    if isinstance(error, RichError):
        if error._message != "" or not error._error:
            return error._message

        return error_message(error._error)

    return str(error)


def error_code(error: Exception) -> int:
    if isinstance(error, RichError):
        if error._code != codes.UNKNOWN_CODE or not error._error:
            return error._code

        return error_code(error._error)

    return 0


def _error_info(error: Exception):
    info = {
        constants.Operation: "",
        constants.Code: codes.UNKNOWN_CODE,
        constants.Message: "",
    }

    if isinstance(error, RichError):
        info[constants.Operation] = error._operation
        info[constants.Message] = error_message(error)
        info[constants.Code] = error_code(error)

        return info

    info[constants.Message] = str(error)

    return info


def get_error_info(error: Exception, error_log: List) -> List:
    info = _error_info(error)
    error_log.append(info)

    if not error._error:
        return error_log

    return get_error_info(error._error, error_log)

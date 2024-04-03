from apps.common.exceptions import CustomException


class RichPadlockLimit(CustomException):
    pass


class PadlockDoesNotExist(CustomException):
    pass


class AccessDeniedPadlockFile(CustomException):
    pass


class AlreadyPadlockBuyErr(CustomException):
    pass

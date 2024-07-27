from apps.common.exceptions import CustomException


class IpBlocked(CustomException):
    pass


class AuthFieldNotAllowedToReceiveSms(CustomException):
    pass


class InvalidCodeErr(CustomException):
    pass

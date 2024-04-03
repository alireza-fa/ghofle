from apps.common.exceptions import CustomException


class GatewayConnectionError(CustomException):
    pass


class GatewayTimeoutError(CustomException):
    pass

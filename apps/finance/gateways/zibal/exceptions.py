from apps.common.exceptions import CustomException


class StatusErr(CustomException):
    pass


class PaymentFailedErr(CustomException):
    pass

from apps.common.exceptions import CustomException


class UserConflictErr(CustomException):
    pass


class TooManyRequestUpdateImageErr(CustomException):
    pass
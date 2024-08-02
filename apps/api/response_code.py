from django.utils.translation import gettext_lazy as _


# 200_00
OK = 200_00
CREATED = 201_00
# 400_00
BAD_REQUEST = 400_00
# 401_00
INVALID_CODE = 401_00
INVALID_OTP = 401_01
INVALID_TOKEN = 401_02
# 403_00
IP_BLOCKED = 403_00
# 404_00
USER_NOT_FOUND = 404_00
PADLOCK_NOT_FOUND = 404_01
GATEWAY_NOT_FOUND = 404_02
PAYMENT_NOT_FOUND = 404_03
# 406_00
NOT_ACCEPTABLE = 406_00
PadlockLimit = 406_02
INVALID_PAYMENT = 406_03
ALREADY_PADLOCK_BUY = 406_04
USER_EXIST = 409_00
OPEN_PADLOCK_FILE_LIMIT = 403_00
# 429_00
TOO_MANY_REQUEST = 429_00
USER_NOT_ALLOW_TO_RECEIVE_SMS = 429_01
TOO_MANY_REQUEST_CHANGE_IMAGE = 429_02
# 5000
INTERNAL_SERVER_ERROR = 500_00
ERROR_UPLOAD = 500_01
GATEWAY_CONNECTION_ERROR = 503_00
GATEWAY_TIMEOUT_ERROR = 504_00


ERROR_TRANSLATION = {
    # 2000
    OK: "Ok",
    CREATED: _("Created a row"),
    # 4000
    INVALID_OTP: "Invalid code",
    TOO_MANY_REQUEST: "Please try again later",
    INVALID_TOKEN: "Invalid token",
    USER_NOT_FOUND: "User with this information not found",
    IP_BLOCKED: "Your IP address has been blocked and you will not be able"
                " to receive the code for a maximum of 24 hours.",
    USER_NOT_ALLOW_TO_RECEIVE_SMS: "You can only receive a code every two minutes",
    INVALID_CODE: "Invalid code",
    PadlockLimit: "You have too many unchecked padlocks",
    PADLOCK_NOT_FOUND: "Padlock with this information not found",
    OPEN_PADLOCK_FILE_LIMIT: "You are limited",
    GATEWAY_NOT_FOUND: "Gateway not found",
    PAYMENT_NOT_FOUND: "Payment not found",
    INVALID_PAYMENT: "Invalid payment",
    ALREADY_PADLOCK_BUY: "Already padlock buy",
    USER_EXIST: "User with this information already exists.",
    TOO_MANY_REQUEST_CHANGE_IMAGE: "The request to change user profile picture has exceeded the limit",
    # 5000
    INTERNAL_SERVER_ERROR: "Interval server error",
    ERROR_UPLOAD: "Error while uploading file",
    GATEWAY_CONNECTION_ERROR: "Gateway connection error",
    GATEWAY_TIMEOUT_ERROR: "Gateway timeout error",
}

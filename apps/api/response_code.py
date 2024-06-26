# 2000
OK = 2000
CREATED = 2010
# 4000
NOT_ACCEPTABLE = 4060
BAD_REQUEST = 4010
IP_BLOCKED = 4030
USER_NOT_FOUND = 4040
PADLOCK_NOT_FOUND = 4041
GATEWAY_NOT_FOUND = 4042
PAYMENT_NOT_FOUND = 4023
INVALID_TOKEN = 4060
INVALID_CODE = 4061
PadlockLimit = 4062
INVALID_PAYMENT = 4063
ALREADY_PADLOCK_BUY = 4064
USER_EXIST = 4065
OPEN_PADLOCK_FILE_LIMIT = 4030
TOO_MANY_REQUEST = 4290
USER_NOT_ALLOW_TO_RECEIVE_SMS = 4291
# 5000
INTERNAL_SERVER_ERROR = 5000
ERROR_UPLOAD = 5001
GATEWAY_CONNECTION_ERROR = 5030
GATEWAY_TIMEOUT_ERROR = 5040

INVALID_OTP = 4061

ERROR_TRANSLATION = {
    # 2000
    OK: "Ok",
    CREATED: "Created a row",
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
    # 5000
    INTERNAL_SERVER_ERROR: "Interval server error",
    ERROR_UPLOAD: "Error while uploading file",
    GATEWAY_CONNECTION_ERROR: "Gateway connection error",
    GATEWAY_TIMEOUT_ERROR: "Gateway timeout error",
}

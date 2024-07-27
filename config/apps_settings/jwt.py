from datetime import timedelta


JWT_AUTH_ACCESS_TOKEN_LIFETIME = timedelta(minutes=10)
JWT_AUTH_REFRESH_TOKEN_LIFETIME = timedelta(days=31)
JWT_AUTH_ENCRYPT_KEY = b'\x102\x1b\xda\xf7\x936\x97\x84\xb4\x1a\xe5h"4\x97;\xbb\x13\xb5\xf3i\r\x9bu\xac{\x92\xa4\x02@S'


JWT_AUTH_ACCESS_TOKEN_CLAIMS = {
    "username": "",
    "phone_number": "",
    "avatar_image_filename": "",
    "is_active": False,
    "is_admin": False,
    "roles": [],
}

JWT_AUTH_ACCESS_TOKEN_USER_FIELD_CLAIMS = {
    "username": "",
    "phone_number": "",
    "avatar_image_filename": "",
    "is_active": False,
    "is_admin": False,
}

JWT_AUTH_GET_USER_BY_ACCESS_TOKEN = True

JWT_AUTH_CACHE_USING = True

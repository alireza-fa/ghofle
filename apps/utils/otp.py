from random import randint

from .cache import get_cache, set_cache, incr_cache


def generate_otp_code() -> str:
    return str(randint(a=100000, b=999999))


def check_number_allow_to_receive_sms(phone_number: str, ip_address: str) -> bool:
    """
     Each number can only receive up to ten SMS for the code every twenty-four hours
    """
    login_info = get_cache(key=phone_number)
    if login_info:
        return False

    has_ip_address = get_cache(key=ip_address)
    if has_ip_address:
        return False

    key = phone_number + 'otp_sms_count'

    sms_receive_count = get_cache(key=key)

    if sms_receive_count:
        if sms_receive_count >= 10:
            # TODO: change sms receive count
            return False
    else:
        set_cache(key=key, value=1, timeout=86400)
        return True

    incr_cache(key=key)

    return True

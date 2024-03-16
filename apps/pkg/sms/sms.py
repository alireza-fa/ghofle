from django.conf import settings

from apps.pkg.sms.dummy.dummy import get_dummy_sms_service


def get_sms_service():
    match settings.SMS_SERVICE_NAME:
        case "dummy":
            return get_dummy_sms_service()

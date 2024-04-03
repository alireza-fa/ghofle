from rest_framework import serializers

from apps.api import response_code
from apps.api.response_code import ERROR_TRANSLATION
from apps.api.serializers import BaseResponseWithErrorSerializer, BaseResponseSerializer


class PaymentNotFoundErrSerializer(BaseResponseWithErrorSerializer):
    code = serializers.IntegerField(default=response_code.PAYMENT_NOT_FOUND)
    error = serializers.CharField(default=ERROR_TRANSLATION[response_code.PAYMENT_NOT_FOUND])


class PaymentVerifyResponseSerializer(BaseResponseSerializer):
    pass


class PaymentStatusErrSerializer(BaseResponseWithErrorSerializer):
    code = serializers.IntegerField(default=response_code.INVALID_PAYMENT)
    error = serializers.CharField(default=ERROR_TRANSLATION[response_code.INVALID_PAYMENT])

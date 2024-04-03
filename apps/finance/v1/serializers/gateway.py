from rest_framework import serializers

from apps.api import response_code
from apps.api.response_code import ERROR_TRANSLATION
from apps.api.serializers import BaseResponseWithErrorSerializer


class GatewayConnectionErrSerializer(BaseResponseWithErrorSerializer):
    code = serializers.IntegerField(default=response_code.GATEWAY_CONNECTION_ERROR)
    error = serializers.CharField(default=ERROR_TRANSLATION[response_code.GATEWAY_CONNECTION_ERROR])


class GatewayTimeoutErrorSerializer(BaseResponseWithErrorSerializer):
    code = serializers.IntegerField(default=response_code.GATEWAY_TIMEOUT_ERROR)
    error = serializers.CharField(default=ERROR_TRANSLATION[response_code.GATEWAY_TIMEOUT_ERROR])

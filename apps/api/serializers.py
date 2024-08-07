from rest_framework import serializers

from apps.api import response_code
from apps.api.response_code import ERROR_TRANSLATION


class BaseResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=2000, min_value=1000, max_value=3999)


class BaseResponseWithErrorSerializer(serializers.Serializer):
    pass


class BaseResponseWithValidationErrorSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=4001)


class InternalServerErrSerializer(BaseResponseWithErrorSerializer):
    code = serializers.IntegerField(default=response_code.INTERNAL_SERVER_ERROR)
    error = serializers.CharField(default=ERROR_TRANSLATION[response_code.INTERNAL_SERVER_ERROR])

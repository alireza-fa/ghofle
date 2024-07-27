from rest_framework import serializers

from apps.api import response_code
from apps.api.serializers import BaseResponseSerializer, BaseResponseWithErrorSerializer


class _GenerateTokenResponse(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()


class GenerateTokenResponse(BaseResponseSerializer):
    token = _GenerateTokenResponse()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(min_length=100)


class AccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField(min_length=100)


class RefreshTokenResponse(BaseResponseSerializer):
    result = AccessTokenSerializer()


class TokenInvalidErrSerializer(BaseResponseWithErrorSerializer):
    code = serializers.IntegerField(default=response_code.INVALID_TOKEN)
    error = serializers.CharField(default=response_code.ERROR_TRANSLATION[response_code.INVALID_TOKEN])


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=100)


class InvalidTokenSerializer(BaseResponseWithErrorSerializer):
    code = serializers.IntegerField(default=response_code.INVALID_TOKEN)
    error = serializers.CharField(default=response_code.ERROR_TRANSLATION[response_code.INVALID_TOKEN])

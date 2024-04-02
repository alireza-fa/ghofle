from rest_framework import serializers


def base_response_serializer(code: int, result: object | None = None) -> object:
    response = {
        "code": code,
        "result": result
    }

    class BaseResponse(serializers.Serializer):
        code = serializers.IntegerField(default=response["code"], min_value=1000, max_value=2999)
        success = serializers.BooleanField(default=False)
        if response["result"]:
            result = response["result"]()

    return BaseResponse


def base_response_with_error_serializer(code: int, error: str | None = None) -> object:
    response = {
        "code": code,
        "error": error
    }

    class BaseResponseWithError(serializers.Serializer):
        code = serializers.IntegerField(default=response["code"], min_value=3000, max_value=5999)
        if response["error"]:
            error = serializers.CharField(default=response["error"])

    return BaseResponseWithError


def base_response_with_validation_error_serializer(error: serializers.Serializer) -> object:
    response = {
        "error": error
    }

    class BaseResponseWithValidationError(serializers.Serializer):
        code = serializers.IntegerField(default=4001)
        error = response["error"]()

    return BaseResponseWithValidationError

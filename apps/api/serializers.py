from rest_framework import serializers


class BaseResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    code = serializers.IntegerField(default=2000, min_value=1000, max_value=3999)


class BaseResponseWithErrorSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)


class BaseResponseWithValidationErrorSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=4001)
    success = serializers.BooleanField(default=False)

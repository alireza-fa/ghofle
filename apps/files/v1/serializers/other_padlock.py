from rest_framework import serializers

from apps.api import response_code
from apps.api.response_code import ERROR_TRANSLATION
from apps.api.serializers import BaseResponseSerializer, BaseResponseWithErrorSerializer
from apps.files.models import Padlock
from apps.pkg.storage.storage import get_storage

storage = get_storage()


class PadlockDetailSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField(method_name="get_thumbnail")
    file = serializers.SerializerMethodField(method_name="get_file")
    is_sell = serializers.SerializerMethodField(method_name="check_sell")
    owner = serializers.SerializerMethodField(method_name="get_owner")

    class Meta:
        model = Padlock
        fields = ("id", "owner", "title", "description", "thumbnail", "file", "review_active", "price", "is_sell")

    def get_thumbnail(self, obj):
        try:
            return storage.get_file_url(filename=obj.thumbnail.filename)
        except Exception:
            return None

    def get_owner(self, obj):
        return obj.owner.username

    def get_file(self, obj):
        if obj.users.filter(user=self.context["request"].user).exists():
            return True
        return False

    def check_sell(self, obj):
        if obj.users.count() > 0:
            return True
        return False


class PadlockOpenFileResponseSerializer(serializers.Serializer):
    file_url = serializers.CharField()


class PadlockBuyResponseSerializer(serializers.Serializer):
    pay_link = serializers.CharField()


class PadlockBuySwaggerResponseSerializer(BaseResponseSerializer):
    result = PadlockBuyResponseSerializer()


class PadlockOtherDetailResponseSerializer(BaseResponseSerializer):
    result = PadlockDetailSerializer()


class PadlockOpenFileSwaggerResponseSerializer(BaseResponseSerializer):
    result = PadlockOpenFileResponseSerializer()


class OpenPadlockFileLimitErrSerializer(BaseResponseWithErrorSerializer):
    code = serializers.IntegerField(default=response_code.OPEN_PADLOCK_FILE_LIMIT)
    error = serializers.CharField(default=ERROR_TRANSLATION[response_code.OPEN_PADLOCK_FILE_LIMIT])


class PadlockPaginationResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    previous = serializers.CharField()
    next = serializers.CharField()
    results = PadlockDetailSerializer()


class PadlockBuyListResponseSerializer(BaseResponseSerializer):
    result = PadlockPaginationResponseSerializer()

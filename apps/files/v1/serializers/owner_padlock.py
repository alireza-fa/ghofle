from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.api import response_code
from apps.api.response_code import ERROR_TRANSLATION
from apps.api.serializers import BaseResponseSerializer, BaseResponseWithErrorSerializer, \
    BaseResponseWithValidationErrorSerializer
from apps.files.models import Padlock
from apps.pkg.storage.storage import get_storage

storage = get_storage()


class PadlockCreateSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(required=False)
    file = serializers.FileField(required=True)
    review_active = serializers.BooleanField(default=True, required=False)

    class Meta:
        model = Padlock
        fields = ("title", "description", "thumbnail", "file", "review_active", "price")

        extra_kwargs = {
            "thumbnail_file": {"write_only": True},
            "file": {"write_only": True}
        }

    def validate_thumbnail(self, thumbnail):
        if thumbnail:
            if thumbnail.size > 1_000_000:
                raise serializers.ValidationError(_("you can just upload thumbnail less than 1.0m"))
            return thumbnail
        return thumbnail

    def validate_file(self, file):
        if file:
            if file.size > 100_000_000:
                raise serializers.ValidationError(_("you can just upload file less than 100m"))
            return file
        return file


class PadlockDetailSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField(method_name="get_thumbnail")
    file = serializers.SerializerMethodField(method_name="get_file")

    class Meta:
        model = Padlock
        fields = ("id", "title", "description", "thumbnail", "file", "review_active",
                  "price", "checked", "is_active", "is_deleted")

    def get_thumbnail(self, obj):
        if obj.is_deleted:
            return None
        try:
            return storage.get_file_url(filename=obj.thumbnail.filename)
        except Exception:
            return None

    def get_file(self, obj):
        if obj.is_deleted:
            return None
        try:
            return storage.get_file_url(filename=obj.file.filename)
        except Exception:
            return None


class PadlockPaginationResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    previous = serializers.CharField()
    next = serializers.CharField()
    results = PadlockDetailSerializer()


class PadlockResponseSerializer(BaseResponseSerializer):
    result = PadlockPaginationResponseSerializer()


class CreatePadlockResponseSerializer(BaseResponseSerializer):
    result = PadlockDetailSerializer()


class CreatePadlockBadRequestSerializer(BaseResponseWithValidationErrorSerializer):
    error = PadlockCreateSerializer()


class FilePutErrorSerializer(BaseResponseWithErrorSerializer):
    code = serializers.IntegerField(default=response_code.ERROR_UPLOAD)
    error = serializers.CharField(default=ERROR_TRANSLATION[response_code.ERROR_UPLOAD])


class RichPadlockLimitErrSerializer(BaseResponseWithErrorSerializer):
    code = serializers.IntegerField(default=response_code.PadlockLimit)
    error = serializers.CharField(default=ERROR_TRANSLATION[response_code.PadlockLimit])


class DeletePadlockResponseSerializer(BaseResponseSerializer):
    pass


class PadlockNotFoundErrSerializer(BaseResponseWithErrorSerializer):
    code = serializers.IntegerField(default=response_code.PADLOCK_NOT_FOUND)
    error = serializers.CharField(default=ERROR_TRANSLATION[response_code.PADLOCK_NOT_FOUND])

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.files.models import Padlock
from apps.pkg.storage.storage import get_storage

storage = get_storage()


class PadlockCreateSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(required=False)
    file = serializers.FileField(required=True)

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
        fields = ("id", "title", "description", "thumbnail", "file", "review_active", "price")

    def get_thumbnail(self, obj):
        try:
            return storage.get_file_url(filename=obj.thumbnail.filename)
        except Exception:
            return None

    def get_file(self, obj):
        try:
            return storage.get_file_url(filename=obj.file.filename)
        except Exception:
            return None

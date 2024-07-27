from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.api.serializers import BaseResponseSerializer
from apps.common.services.storage import get_file_url

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    avatar_image = serializers.SerializerMethodField(method_name="get_avatar_image", read_only=True)

    class Meta:
        model = User
        fields = ("username", "phone_number", "avatar_image")

    def get_avatar_image(self, obj):
        return obj.avatar_image_filename


class ProfileResponseSerializer(BaseResponseSerializer):
    result = ProfileSerializer()


class ProfileBaseUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username",)


class ProfileBaseUpdateResponseSerializer(BaseResponseSerializer):
    result = ProfileBaseUpdateSerializer()


class ProfileUpdateAvatarImageSerializer(serializers.Serializer):
    avatar_image = serializers.ImageField()

    def validate_avatar_image(self, avatar_image):
        if avatar_image.size > 500_000:
            raise serializers.ValidationError(_("you can just upload file less than 0.5m"))
        return avatar_image


class _ProfileUpdateAvatarImageResponse(serializers.Serializer):
    avatar_image = serializers.CharField(default="avatar image link")


class ProfileUpdateAvatarImageResponse(BaseResponseSerializer):
    result = _ProfileUpdateAvatarImageResponse()

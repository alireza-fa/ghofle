from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.api.serializers import BaseResponseSerializer
from apps.common.storage import get_file_url

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    avatar_image = serializers.SerializerMethodField(method_name="get_avatar_image", read_only=True)

    class Meta:
        model = User
        fields = ("username", "phone_number", "avatar_image")

    def get_avatar_image(self, obj):
        if obj.avatar_image:
            try:
                return get_file_url(filename=obj.avatar_image.filename, log_properties={})
            except:
                return None
        return None


class ProfileResponseSerializer(BaseResponseSerializer):
    result = ProfileSerializer()


class ProfileBaseUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username",)


class ProfileBaseUpdateResponseSerializer(BaseResponseSerializer):
    result = ProfileBaseUpdateSerializer()

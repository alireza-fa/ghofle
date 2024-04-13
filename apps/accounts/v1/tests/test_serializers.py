import uuid

from rest_framework.test import APITestCase

from apps.accounts.models import BaseUser
from apps.common.models import File
from apps.accounts.v1.serializers.profile import ProfileSerializer


class TestSerializers(APITestCase):
    def setUp(self):
        self.user = BaseUser.objects.create_user(username="alireza", phone_number="09129121111")

    def test_profile_serializer_with_avatar_image(self):
        file = File.objects.create(filename="%s.%s" % (uuid.uuid4(), "png"), size=24000)
        self.user.avatar_image = file
        self.user.save()

        serializer = ProfileSerializer(instance=self.user)
        self.assertIsNotNone(serializer.data.get("avatar_image"))

    def test_profile_serializer_without_avatar_image(self):
        serializer = ProfileSerializer(instance=self.user)
        self.assertIsNone(serializer.data.get("avatar_image"))

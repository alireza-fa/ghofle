import uuid
from datetime import timedelta
from random import randint

from django.test import TestCase
from django.utils.timezone import now

from apps.accounts.models import BaseUser
from apps.common.models import File


class TestBaseUser(TestCase):
    def setUp(self):
        self.username = "alireza"
        self.phone_number = "09129121111"

    def test_create_base_user(self):
        user = BaseUser.objects.create_user(username=self.username, phone_number=self.phone_number)
        self.assertEqual(BaseUser.objects.count(), 1)

    def test_create_user_with_password(self):
        user = BaseUser.objects.create_user(username=self.username, phone_number=self.phone_number, password="password")
        self.assertEqual(user.check_password("password"), True)

    def test_create_username(self):
        user = BaseUser.objects.create_user(username=self.username, phone_number=self.phone_number)
        self.assertEqual(user.username, self.username)

    def test_create_phone_number(self):
        user = BaseUser.objects.create_user(username=self.username, phone_number=self.phone_number)
        self.assertEqual(user.phone_number, self.phone_number)

    def test_create_avatar_image(self):
        avatar_image = File.objects.create(filename="%s.png" % uuid.uuid4(), size=25000)
        user = BaseUser.objects.create_user(username=self.username, phone_number=self.phone_number)
        user.avatar_image = avatar_image
        user.save()

        self.assertEqual(user.avatar_image, avatar_image)

    def test_create_last_image_update(self):
        before = now() - timedelta(seconds=1)
        user = BaseUser.objects.create_user(username=self.username, phone_number=self.phone_number)
        user.last_image_update = now()
        user.save()
        after = now() + timedelta(seconds=1)

        self.assertLess(user.last_image_update, after)
        self.assertGreater(user.last_image_update, before)

    def test_create_user_permissions(self):
        user = BaseUser.objects.create_user(username=self.username, phone_number=self.phone_number)
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_admin, False)
        self.assertEqual(user.is_superuser, False)

    def test_create_admin_permissions(self):
        user = BaseUser.objects.create_admin(username=self.username, phone_number=self.phone_number)
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_admin, True)
        self.assertEqual(user.is_superuser, False)

    def test_create_is_superuser_permissions(self):
        user = BaseUser.objects.create_superuser(username=self.username, phone_number=self.phone_number)
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_admin, True)
        self.assertEqual(user.is_superuser, True)

    def test_queries_user(self):
        file = File.objects.create(filename="%s.png" % uuid.uuid4(), size=25000)
        for i in range(100):
            BaseUser.objects.create(username="%s-%s" % (self.username, i),
                                    phone_number=str(randint(10000000000, 99999999999)),
                                    avatar_image=file)

        with self.assertNumQueries(1):
            [u.avatar_image for u in BaseUser.objects.all()]

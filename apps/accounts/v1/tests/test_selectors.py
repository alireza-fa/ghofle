from django.test import TestCase

from apps.accounts.models import BaseUser
from apps.accounts.v1.selectors.base_user import get_user_by_phone_number, get_user_by_username
from apps.accounts.v1.selectors.profile import get_profile_user


class TestSelectors(TestCase):
    def setUp(self):
        self.user = BaseUser.objects.create_user(username="alireza", phone_number="09129121111")

    def test_get_user_by_phone_number(self):
        user = get_user_by_phone_number(phone_number=self.user.phone_number)
        self.assertEqual(user, self.user)

    def test_get_user_by_username(self):
        user = get_user_by_username(username=self.user.username)
        self.assertEqual(user, self.user)

    def test_get_profile_user(self):
        profile = get_profile_user(user_id=self.user.id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile, self.user)

    def test_get_profile_not_found(self):
        with self.assertRaises(BaseUser.DoesNotExist):
            get_profile_user(user_id=4)

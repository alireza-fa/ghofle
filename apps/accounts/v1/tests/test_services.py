from django.test import TestCase

from apps.accounts.v1.services.base_user import create_base_user
from apps.accounts.models import BaseUser


class TestServices(TestCase):

    def test_create_base_user(self):
        create_base_user(username="alireza", phone_number="09129121111")
        self.assertEqual(BaseUser.objects.count(), 1)

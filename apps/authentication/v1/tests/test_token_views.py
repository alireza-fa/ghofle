import time
from typing import Dict

from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.contrib.auth import get_user_model
from django.test import override_settings

from apps.authentication.v1.services.token import generate_token
from apps.utils import client
from apps.authentication.v1.views.token import VerifyTokenView
from apps.utils.cache import clear_all_cache

User = get_user_model()


class TestTokenViews(APITestCase):
    def setUp(self):
        self.username = "alireza"
        self.phone_number = "09129121111"
        self.user = User.objects.create_user(username=self.username, phone_number=self.phone_number)
        self.client_info = {client.IP_ADDRESS: "127.0.0.1", client.DEVICE_NAME: "test-device"}

    def get_token(self, user: User) -> Dict:
        return generate_token(client_info=self.client_info, user=user)

    def test_verify_token_access_token_200(self):
        clear_all_cache()
        token = self.get_token(user=self.user)
        request = APIRequestFactory().post(path="auth_v1:verify_token", data={
            "token": token["access_token"]
        })
        request.META["REMOTE_ADDR"] = self.client_info[client.IP_ADDRESS]
        request.META["HTTP_USER_AGENT"] = self.client_info[client.DEVICE_NAME]
        res = VerifyTokenView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_verify_token_refresh_token_200(self):
        clear_all_cache()
        token = self.get_token(user=self.user)
        request = APIRequestFactory().post(path="auth_v1:verify_token", data={
            "token": token["refresh_token"]
        })
        request.META["REMOTE_ADDR"] = self.client_info[client.IP_ADDRESS]
        request.META["HTTP_USER_AGENT"] = self.client_info[client.DEVICE_NAME]
        res = VerifyTokenView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_verify_token_401(self):
        request = APIRequestFactory().post(path="auth_v1:verify_token")
        res = VerifyTokenView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_token_access_token_406_expire(self):
        token = generate_token(client_info=self.client_info, user=self.user)
        request = APIRequestFactory().post(path="auth_v1:verify_token", data={
            "token": token["access_token"]
        })
        request.META["REMOTE_ADDR"] = self.client_info[client.IP_ADDRESS]
        request.META["HTTP_USER_AGENT"] = self.client_info[client.DEVICE_NAME]
        res = VerifyTokenView.as_view()(request).render()
        time.sleep(10)
        self.assertEqual(res.status_code, status.HTTP_406_NOT_ACCEPTABLE)

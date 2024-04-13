from rest_framework.test import APITestCase, APIRequestFactory

from apps.accounts.models import BaseUser
from apps.accounts.v1.views.profile import ProfileView
from apps.authentication.v1.services.token import generate_token
from apps.utils import client


class TestViews(APITestCase):

    def test_profile_view(self):
        user = BaseUser.objects.create_user(username="alireza", phone_number="09129121111", password="password")

        token = generate_token(user=user, client_info={client.IP_ADDRESS: "127.0.0.1", client.DEVICE_NAME: "test-device"})
        request = (APIRequestFactory(
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token["access_token"]}'})
                   .get(path="accounts_v1:profile"))
        request.META["REMOTE_ADDR"] = "127.0.0.1"
        request.META["HTTP_USER_AGENT"] = "test-device"
        res = ProfileView.as_view()(request).render()
        self.assertEqual(res.status_code, 200)

    def test_profile_view_not_exist_user(self):
        user = BaseUser.objects.create_user(username="alireza", phone_number="09129121111")

        token = generate_token(user=user, client_info={client.IP_ADDRESS: "127.0.0.1", client.DEVICE_NAME: "test-device"})
        user.delete()
        request = (APIRequestFactory(
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token["access_token"]}'})
                   .get(path="accounts_v1:profile"))
        request.META["REMOTE_ADDR"] = "127.0.0.1"
        request.META["HTTP_USER_AGENT"] = "test-device"
        res = ProfileView.as_view()(request).render()
        self.assertEqual(res.status_code, 404)

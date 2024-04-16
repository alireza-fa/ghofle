from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from apps.api import response_code
from apps.authentication.v1.views.sign_user import LoginByPhoneNumberView, VerifySignUserView, RegisterView, \
    RegisterView
from apps.utils.cache import clear_all_cache, delete_cache, get_cache
from apps.authentication.v1.services.sign_user import SIGN_SUF_KEY


User = get_user_model()


class TestViews(APITestCase):
    def setUp(self):
        self.username = "alireza"
        self.phone_number = "09129121111"
        self.password = "password"
        self.user = User.objects.create_user(username=self.username, phone_number=self.phone_number,
                                             password=self.password)

    def test_login_by_phone_number_200(self):
        clear_all_cache()
        request = APIRequestFactory().post(path="auth_v1:login_by_phone_number", data={
            "phone_number": self.phone_number,
        })
        res = LoginByPhoneNumberView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNone(res.data["result"])
        self.assertTrue(res.data["success"])
        self.assertEqual(res.data["code"], response_code.OK)

    def test_login_by_phone_number_400(self):
        clear_all_cache()
        request = APIRequestFactory().post(path="auth_v1:login_by_phone_number", data={
            "phone_number": "91291211141",
        })
        res = LoginByPhoneNumberView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(res.data["error"]["phone_number"])

    def test_login_by_phone_number_403(self):
        clear_all_cache()
        request = APIRequestFactory().post(path="auth_v1:login_by_phone_number", data={
            "phone_number": self.phone_number,
        })

        for i in range(11):
            LoginByPhoneNumberView.as_view()(request)
            delete_cache(key=self.phone_number + SIGN_SUF_KEY)
        res = LoginByPhoneNumberView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_by_phone_number_404(self):
        clear_all_cache()
        requests = APIRequestFactory().post(path="auth_v1:login_by_phone_number", data={
            "phone_number": "09129121122"
        })
        res = LoginByPhoneNumberView.as_view()(requests).render()
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_by_phone_number_429(self):
        clear_all_cache()
        request = APIRequestFactory().post(path="auth_v1:login_by_phone_number", data={
            "phone_number": self.phone_number,
        })

        LoginByPhoneNumberView.as_view()(request).render()
        res = LoginByPhoneNumberView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertFalse(res.data["success"])
        self.assertEqual(res.data["code"], response_code.USER_NOT_ALLOW_TO_RECEIVE_SMS)

    def test_verify_sign_user_login_200(self):
        clear_all_cache()
        request = APIRequestFactory().post(path="auth_v1:login_by_phone_number", data={
            "phone_number": self.phone_number
        })
        LoginByPhoneNumberView.as_view()(request).render()

        cache_info = get_cache(key=self.phone_number + SIGN_SUF_KEY)
        request = APIRequestFactory().post(path="auth_v1:verify", data={
            "phone_number": self.phone_number,
            "code": cache_info["code"],
        })
        res = VerifySignUserView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res.data["result"]["access_token"])
        self.assertIsNotNone(res.data["result"]["refresh_token"])

    def test_verify_sign_user_register_200(self):
        clear_all_cache()
        phone_number = "09129121212"
        request = APIRequestFactory().post(path="auth_v1:register", data={
            "username": "mahsa",
            "phone_number": phone_number,
        })
        RegisterView.as_view()(request).render()
        cache_info = get_cache(key=phone_number + SIGN_SUF_KEY)
        request = APIRequestFactory().post(path="auth_v1:verify", data={
            "phone_number": phone_number,
            "code": cache_info["code"],
        })
        res = VerifySignUserView.as_view()(request)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res.data["result"]["access_token"])
        self.assertIsNotNone(res.data["result"]["refresh_token"])

    def test_verify_sign_user_400(self):
        clear_all_cache()
        request = APIRequestFactory().post(path="auth_v1:verify", data={
            "phone_number": self.phone_number,
            "code": "invalid code"
        })
        res = VerifySignUserView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data["success"])

    def test_verify_sign_user_404(self):
        clear_all_cache()
        request = APIRequestFactory().post(path="auth_v1:login_by_phone_number", data={
            "phone_number": self.phone_number,
        })
        LoginByPhoneNumberView.as_view()(request).render()
        self.user.delete()
        cache_info = get_cache(key=self.phone_number + SIGN_SUF_KEY)
        request = APIRequestFactory().post(path="auth_v1:verify", data={
            "phone_number": self.phone_number,
            "code": cache_info["code"]
        })
        res = VerifySignUserView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_verify_sign_user_406(self):
        clear_all_cache()
        request = APIRequestFactory().post(path="auth_v1:login_by_phone_number", data={
            "phone_number": self.phone_number
        })
        LoginByPhoneNumberView.as_view()(request).render()
        cache_info = get_cache(key=self.phone_number + SIGN_SUF_KEY)
        request = APIRequestFactory().post(path="auth_v1:verify", data={
            "phone_number": self.phone_number,
            "code": int(cache_info["code"]) + 1 if int(cache_info["code"]) > 999999 else int(cache_info["code"]) - 1
        })
        res = VerifySignUserView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_verify_sign_user_409(self):
        clear_all_cache()
        phone_number = "09129121122"
        username = "mahsa"
        request = APIRequestFactory().post(path="auth_v1:register", data={
            "username": username,
            "phone_number": phone_number,
        })
        RegisterView.as_view()(request).render()
        cache_info = get_cache(key=phone_number + SIGN_SUF_KEY)
        User.objects.create_user(username=username, phone_number=phone_number)
        request = APIRequestFactory().post(path="auth_v1:verify", data={
            "phone_number": phone_number,
            "code": cache_info["code"],
        })
        res = VerifySignUserView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)

    def test_register_200(self):
        clear_all_cache()
        request = APIRequestFactory().post(path="auth_v1:register", data={
            "username": "mahsa",
            "phone_number": "password",
        })
        res = RegisterView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNone(res.data["result"])

    def test_register_400(self):
        request = APIRequestFactory().post(path="auth_v1:register", data={
            "username": self.username,
            "phone_number": self.phone_number,
        })
        res = RegisterView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["code"], response_code.BAD_REQUEST)
        self.assertEqual(len(res.data["error"]), 2)

    def test_register_400_2(self):
        request = APIRequestFactory().post(path="auth_v1:register", data={
            "username": "mahsa",
            "phone_number": self.phone_number,
        })
        res = RegisterView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(res.data["error"]), 1)

    def test_register_403(self):
        clear_all_cache()
        phone_number = "09129121122"
        request = APIRequestFactory().post(path="auth_v1:register", data={
            "username": "mahsa",
            "phone_number": phone_number,
        })

        for i in range(11):
            RegisterView.as_view()(request)
            delete_cache(key=phone_number + SIGN_SUF_KEY)
        res = RegisterView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_register_429(self):
        clear_all_cache()
        request = APIRequestFactory().post(path="auth_v1:register", data={
            "username": "mahsa",
            "phone_number": "09129121122",
        })
        RegisterView.as_view()(request)
        res = RegisterView.as_view()(request).render()
        self.assertEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

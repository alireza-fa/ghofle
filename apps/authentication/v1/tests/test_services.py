from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from django.contrib.auth import get_user_model

from apps.authentication.exceptions import InvalidCode, AuthFieldNotAllowedToReceiveSms, IpBlocked
from apps.authentication.v1.services.sign_user import login_by_password, check_ip_address_access, \
    check_auth_field_allow_to_receive_sms, SIGN_SUF_KEY, login_by_phone_number, check_validate_auth_field_for_verify, \
    login_state, register_user, register_state, verify_sign_user
from apps.utils import client
from apps.utils.cache import clear_all_cache, get_cache

User = get_user_model()


class TestServices(TestCase):
    def setUp(self):
        self.username = "alireza"
        self.phone_number = "09129121111"
        self.password = "password"
        self.user = User.objects.create_user(username=self.username, phone_number=self.phone_number, password=self.password)
        self.request = APIRequestFactory().get("/")
        self.request.META['REMOTE_ADDR'] = "127.0.0.1"
        self.request.META["HTTP_USER_AGENT"] = "test-device"
        self.client_info = {client.IP_ADDRESS: "127.0.0.1", client.DEVICE_NAME: "test-device"}

    def test_login_by_password_valid_data(self):
        token = login_by_password(request=self.request, username=self.username, password=self.password)
        self.assertEqual(len(token), 2)

    def test_login_by_password_with_invalid_data(self):
        with self.assertRaises(User.DoesNotExist):
            login_by_password(request=self.request, username=self.username, password="invalid_password")

    def test_check_ip_address_access(self):
        ip_address = "127.0.0.1"
        self.assertTrue(check_ip_address_access(ip_address=ip_address))

    def test_check_ip_address_access_false(self):
        ip_address = "127.0.0.1"
        for _ in range(10):
            check_ip_address_access(ip_address=ip_address)

        self.assertFalse(check_ip_address_access(ip_address=ip_address))

    def test_check_auth_field_allow_to_receive_sms(self):
        clear_all_cache()

        auth_field = self.phone_number + SIGN_SUF_KEY
        client_info = {client.IP_ADDRESS: "127.0.0.1", client.DEVICE_NAME: "test-device"}
        self.assertIsNone(check_auth_field_allow_to_receive_sms(auth_field=auth_field, client_info=client_info))

        login_by_phone_number(request=self.request, phone_number=self.phone_number)

        self.assertFalse(check_auth_field_allow_to_receive_sms(auth_field=auth_field, client_info=client_info))

    def test_login_by_phone_number(self):
        clear_all_cache()

        self.assertIsNone(login_by_phone_number(request=self.request, phone_number=self.phone_number))
        self.assertIsNotNone(get_cache(key=self.phone_number+SIGN_SUF_KEY))

    def test_login_by_phone_number_not_exist_phone(self):
        with self.assertRaises(User.DoesNotExist):
            login_by_phone_number(request=self.request, phone_number="09129654858")

    def test_validate_auth_field_for_verify(self):
        clear_all_cache()

        login_by_phone_number(request=self.request, phone_number=self.phone_number)

        self.assertIsNone(check_validate_auth_field_for_verify(auth_field=self.phone_number, client_info=self.client_info))

        for i in range(4):
            check_validate_auth_field_for_verify(auth_field=self.phone_number, client_info=self.client_info)

        with self.assertRaises(InvalidCode):
            check_validate_auth_field_for_verify(auth_field=self.phone_number, client_info=self.client_info)

    def test_login_state(self):
        token = login_state(client_info=self.client_info, phone_number=self.phone_number)
        self.assertEqual(len(token), 2)

    def test_login_state_not_exist_phone(self):
        with self.assertRaises(User.DoesNotExist):
            login_state(client_info=self.client_info, phone_number="09129122222")

    def test_register_user(self):
        clear_all_cache()
        register_user(request=self.request, username="mahsa", phone_number="09129121122", password="password")
        self.assertIsNotNone(get_cache(key="09129121122" + SIGN_SUF_KEY))

    def test_register_user_not_allow_receive_sms(self):
        clear_all_cache()

        register_user(request=self.request, username=self.username, phone_number=self.phone_number, password="password")
        with self.assertRaises(AuthFieldNotAllowedToReceiveSms):
            register_user(request=self.request, username=self.username,
                          phone_number=self.phone_number, password="password")

    def test_register_user_ip_blocked(self):
        clear_all_cache()

        for i in range(11):
            check_ip_address_access(ip_address=self.client_info[client.IP_ADDRESS])

        with self.assertRaises(IpBlocked):
            register_user(request=self.request, username=self.username,
                          phone_number=self.phone_number, password=self.password)

    def test_register_state_validation_error(self):
        with self.assertRaises(ValidationError):
            register_state(client_info=self.client_info, username=self.username,
                           phone_number=self.phone_number, password=self.password)

    def test_verify_sign_user_login_state(self):
        clear_all_cache()
        login_by_phone_number(request=self.request, phone_number=self.phone_number)
        cache_info = get_cache(key=self.phone_number + SIGN_SUF_KEY)
        token = verify_sign_user(request=self.request, phone_number=self.phone_number, code=cache_info["code"])
        self.assertEqual(len(token), 2)
        self.assertIsNotNone(token["access_token"])
        self.assertIsNotNone(token["refresh_token"])

    def test_verify_sign_user_register_state(self):
        clear_all_cache()
        register_user(request=self.request, username="mahsa", phone_number="09129121122", password="password")
        cache_info = get_cache(key="09129121122" + SIGN_SUF_KEY)
        token = verify_sign_user(request=self.request, phone_number="09129121122", code=cache_info["code"])
        self.assertEqual(len(token), 2)
        self.assertIsNotNone(token["access_token"])
        self.assertIsNotNone(token["refresh_token"])

    def test_verify_sign_user_invalid_code(self):
        clear_all_cache()
        login_by_phone_number(request=self.request, phone_number=self.phone_number)
        cache_info = get_cache(key=self.phone_number + SIGN_SUF_KEY)
        code = str(int(cache_info["code"]) + 1)
        with self.assertRaises(InvalidCode):
            verify_sign_user(request=self.request, phone_number=self.phone_number, code=code)

    def test_verify_sign_user_invalid_user_auth_cache(self):
        clear_all_cache()
        with self.assertRaises(InvalidCode):
            verify_sign_user(request=self.request, phone_number=self.phone_number, code="145123")

    def test_verify_sign_user_invalid_for_verify(self):
        clear_all_cache()

        login_by_phone_number(request=self.request, phone_number=self.phone_number)
        cache_info = get_cache(key=self.phone_number + SIGN_SUF_KEY)

        for i in range(5):
            check_validate_auth_field_for_verify(auth_field=self.phone_number, client_info=self.client_info)

        with self.assertRaises(InvalidCode):
            verify_sign_user(request=self.request, phone_number=self.phone_number, code=cache_info["code"])

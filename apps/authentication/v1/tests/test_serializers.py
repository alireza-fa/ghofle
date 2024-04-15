from rest_framework.test import APISimpleTestCase

from apps.authentication.v1.serializers.sign_user import LoginByPhoneNumberSerializer


class TestSignUserSerializer(APISimpleTestCase):

    def test_login_by_phone_number_with_invalid_data(self):
        serializer = LoginByPhoneNumberSerializer(data={"phone_number": "9807654736"})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)

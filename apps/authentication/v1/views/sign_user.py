from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.views import APIView

from apps.accounts.v1.serializers.user import UserNotFoundErrorSerializer
from apps.api import response_code
from apps.api.response import base_response_with_error, base_response
from apps.authentication.v1.services.sign_user import register_user, login_by_phone_number, verify_sign_user_by_code
from apps.authentication.v1.serializers.sign_user import RegisterSerializer, \
    LoginByPhoneNumberSerializer, VerifySignUserSerializer, IpBlockedErrorSerializer, \
    AuthFieldNotAllowedToReceiveSmsErrorSerializer, LoginByPhoneNumberResponseSerializer, \
    VerifySignUserResponseSerializer, InvalidCodeErrSerializer, RegisterResponseSerializer, UserExistSerializer
from apps.authentication import exceptions
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.utils import OpenApiRequest, OpenApiResponse

from apps.api.swagger_fields import PHONE_NUMBER_DESCRIPTION, REGISTER_EXAMPLE_VALUE, \
    LOGIN_BY_PHONE_NUMBER_EXAMPLE_VALUE, LOGIN_BY_PHONE_NUMBER_200_DESCRIPTION, IP_BLOCKED_DESCRIPTION, \
    VERIFY_SIGN_EXAMPLE_VALUE, OTP_CODE_DESCRIPTION, USERNAME_DESCRIPTION, REGISTER_201_DESCRIPTION


SCHEMA_TAGS = ("Auth",)
User = get_user_model()


class LoginByPhoneNumberView(APIView):
    serializer_class = LoginByPhoneNumberSerializer

    @extend_schema(
        request=OpenApiRequest(request=LoginByPhoneNumberSerializer, examples=[
            OpenApiExample(name="phone_number", value=LOGIN_BY_PHONE_NUMBER_EXAMPLE_VALUE, description=PHONE_NUMBER_DESCRIPTION)]),
        responses={
            200: OpenApiResponse(response=LoginByPhoneNumberResponseSerializer, description=LOGIN_BY_PHONE_NUMBER_200_DESCRIPTION),
            400: OpenApiResponse(response=LoginByPhoneNumberSerializer, description="bad request"),
            403: OpenApiResponse(response=IpBlockedErrorSerializer, description=IP_BLOCKED_DESCRIPTION),
            404: OpenApiResponse(response=UserNotFoundErrorSerializer),
            429: OpenApiResponse(response=AuthFieldNotAllowedToReceiveSmsErrorSerializer)},
        tags=SCHEMA_TAGS)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            login_by_phone_number(request=request, phone_number=serializer.validated_data["phone_number"])
        except Exception as ex:
            return base_response_with_error(err=ex)

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK)


class VerifySignUserView(APIView):
    serializer_class = VerifySignUserSerializer

    @extend_schema(
        request=OpenApiRequest(request=VerifySignUserSerializer, examples=[
            OpenApiExample(name="code", value=VERIFY_SIGN_EXAMPLE_VALUE, description=OTP_CODE_DESCRIPTION,),
            OpenApiExample(name="phone_number", value=VERIFY_SIGN_EXAMPLE_VALUE, description=PHONE_NUMBER_DESCRIPTION)]),
        responses={
            200: OpenApiResponse(response=VerifySignUserResponseSerializer),
            400: OpenApiResponse(response=VerifySignUserSerializer),
            401: OpenApiResponse(response=InvalidCodeErrSerializer),
            404: OpenApiResponse(response=UserNotFoundErrorSerializer),
            409: OpenApiResponse(response=UserExistSerializer),
        },
        tags=SCHEMA_TAGS)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            vd = serializer.validated_data
            token = verify_sign_user_by_code(request=request, auth_field=vd["phone_number"], code=vd["code"])
        except Exception as ex:
            return base_response_with_error(err=ex)

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=token)


class RegisterView(APIView):
    serializer_class = RegisterSerializer

    @extend_schema(
        request=OpenApiRequest(request=RegisterSerializer, examples=[
            OpenApiExample(name="username", value=REGISTER_EXAMPLE_VALUE, description=USERNAME_DESCRIPTION),
            OpenApiExample(name="phone_number", value=REGISTER_EXAMPLE_VALUE, description=PHONE_NUMBER_DESCRIPTION)]),
        responses={
            201: OpenApiResponse(response=RegisterResponseSerializer, description=REGISTER_201_DESCRIPTION),
            400: OpenApiResponse(response=RegisterSerializer),
            403: OpenApiResponse(response=IpBlockedErrorSerializer, description=IP_BLOCKED_DESCRIPTION),
            429: OpenApiResponse(response=AuthFieldNotAllowedToReceiveSmsErrorSerializer)
        },
        tags=SCHEMA_TAGS)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            register_user(request=request, **serializer.validated_data)
        except Exception as ex:
            return base_response_with_error(err=ex)

        return base_response(status_code=status.HTTP_201_CREATED, code=response_code.OK)

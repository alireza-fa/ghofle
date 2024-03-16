from rest_framework import status
from rest_framework.views import APIView

from apps.api import response_code
from apps.api.response import base_response_with_error, base_response, base_response_with_validation_error
from apps.authentication.services.sign_user import login_by_password, register_user, login_by_phone_number
from apps.pkg.logger.logger import new_logger
from ..serializers.sign_user import (UserLoginByPasswordSerializer, AuthenticatedResponseSerializer, RegisterSerializer,
                                     LoginByPhoneNumberSerializer,)
from apps.authentication import exceptions
from drf_spectacular.utils import extend_schema


logger = new_logger()


class UserLoginByPasswordView(APIView):
    serializer_class = UserLoginByPasswordSerializer

    @extend_schema(request=UserLoginByPasswordSerializer, responses=AuthenticatedResponseSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                token = login_by_password(request=request, username=serializer.validated_data["username"],
                                          password=serializer.validated_data["password"])
            except ValueError:
                return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND,
                                                code=response_code.USER_NOT_FOUND)

            return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=token)

        return base_response_with_validation_error(error=serializer.errors)


class LoginByPhoneNumberView(APIView):
    serializer_class = LoginByPhoneNumberSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                login_by_phone_number(request=request, phone_number=serializer.validated_data["phone_number"])
            except exceptions.IpBlocked:
                return base_response_with_error(status_code=status.HTTP_403_FORBIDDEN, code=response_code.IP_BLOCKED)
            except exceptions.UserNotFound:
                return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.USER_NOT_FOUND)
            except exceptions.AuthFieldNotAllowedToReceiveSms:
                return base_response_with_error(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                                code=response_code.USER_NOT_ALLOW_TO_RECEIVE_SMS)

            return base_response(status_code=status.HTTP_200_OK, code=response_code.OK)

        return base_response_with_validation_error(error=serializer.errors)


class RegisterView(APIView):
    serializer_class = RegisterSerializer

    @extend_schema(request=RegisterSerializer, responses=None)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                vd = serializer.validated_data
                token = register_user(request=request, username=vd["username"],
                                      email=vd["email"], password=vd["password"])
            except:
                return base_response_with_error(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                code=response_code.INTERNAL_SERVER_ERROR)

            return base_response(status_code=status.HTTP_201_CREATED, code=response_code.CREATED, result=token)

        return base_response_with_validation_error(error=serializer.errors)

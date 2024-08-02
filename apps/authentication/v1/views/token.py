from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiResponse

from apps.accounts.v1.serializers.user import UserNotFoundErrorSerializer
from apps.authentication.v1.serializers.token import TokenSerializer, RefreshTokenSerializer, InvalidTokenSerializer, \
    RefreshTokenResponse
from apps.api.response import base_response, base_response_with_error
from apps.api import response_code
from apps.authentication.v1.services.token import token_verify, token_refresh, token_ban


User = get_user_model()
SCHEMA_TAGS = ("Token",)


class RefreshAccessToken(APIView):
    serializer_class = RefreshTokenSerializer

    @extend_schema(
        request=OpenApiRequest(request=RefreshTokenSerializer),
        responses={
            200: OpenApiResponse(response=RefreshTokenResponse),
            400: OpenApiResponse(response=RefreshTokenSerializer),
            401: OpenApiResponse(response=InvalidTokenSerializer),
            404: OpenApiResponse(response=UserNotFoundErrorSerializer),
        },
        tags=SCHEMA_TAGS)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            access_token = token_refresh(request=request, raw_refresh_token=serializer.validated_data["refresh_token"])
        except Exception as ex:
            return base_response_with_error(err=ex)

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result={"access_token": access_token})


class VerifyTokenView(APIView):
    serializer_class = TokenSerializer

    @extend_schema(
        request=OpenApiRequest(request=TokenSerializer),
        responses={
            200: OpenApiResponse(response=None),
            400: OpenApiResponse(response=TokenSerializer),
            401: OpenApiResponse(response=InvalidTokenSerializer),
        },
        tags=SCHEMA_TAGS)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if token_verify(request=request, raw_token=serializer.validated_data["token"]):
            return Response(status=status.HTTP_200_OK)

        return base_response(status_code=status.HTTP_401_UNAUTHORIZED, code=response_code.INVALID_TOKEN)


class BanRefreshTokenView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=OpenApiRequest(request=RefreshTokenSerializer),
        responses={
            204: OpenApiResponse(response=None),
            401: OpenApiResponse(response=None),
        },
        tags=SCHEMA_TAGS)
    def post(self, request):
        token_ban(request=request)

        return Response(status=status.HTTP_204_NO_CONTENT)

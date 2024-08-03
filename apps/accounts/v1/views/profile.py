from d_jwt_auth.models import UserAuth
from d_jwt_auth.services import update_user_auth_uuid
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiRequest, OpenApiExample
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.accounts.v1.serializers.profile import ProfileSerializer, ProfileBaseUpdateSerializer, \
    ProfileResponseSerializer, ProfileBaseUpdateResponseSerializer, ProfileUpdateAvatarImageSerializer, \
    ProfileUpdateAvatarImageResponse
from apps.accounts.v1.serializers.user import UserNotFoundErrorSerializer
from apps.accounts.v1.services.profile import update_profile_avatar_image
from apps.api import response_code
from apps.api.response import base_response, base_response_with_error
from apps.api.serializers import InternalServerErrSerializer
from apps.api.swagger_fields import USERNAME_DESCRIPTION, BASE_USER_UPDATE_EXAMPLE_VALUE


User = get_user_model()
SCHEMA_TAGS = ("Accounts",)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    @extend_schema(
        responses={
            200: OpenApiResponse(response=ProfileResponseSerializer),
        },
        tags=SCHEMA_TAGS)
    def get(self, request):
        serializer = self.serializer_class(instance=request.user)

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=serializer.data)


class ProfileBaseUpdateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileBaseUpdateSerializer

    @extend_schema(
        request=OpenApiRequest(request=ProfileBaseUpdateSerializer, examples=[
            OpenApiExample(name="username", value=BASE_USER_UPDATE_EXAMPLE_VALUE, description=USERNAME_DESCRIPTION)
        ]),
        responses={
            200: OpenApiResponse(response=ProfileBaseUpdateResponseSerializer),
            404: OpenApiResponse(response=UserNotFoundErrorSerializer)
        },
        tags=SCHEMA_TAGS)
    def patch(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except Exception as ex:
            return base_response_with_error(err=ex)

        serializer = self.serializer_class(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.update(instance=user, validated_data=serializer.validated_data)
        update_user_auth_uuid(user_id=request.user.id, token_type=UserAuth.ACCESS_TOKEN)

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=serializer.data)


class ProfileUpdateAvatarImageView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileUpdateAvatarImageSerializer

    @extend_schema(
        request=OpenApiRequest(request=serializer_class),
        responses={
            200: OpenApiResponse(response=ProfileUpdateAvatarImageResponse),
            500: OpenApiResponse(response=InternalServerErrSerializer)
        },
        tags=SCHEMA_TAGS
    )
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            avatar_link = update_profile_avatar_image(request=request, avatar_image=serializer.validated_data["avatar_image"])
        except Exception as ex:
            return base_response_with_error(err=ex)

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result={"avatar_image": avatar_link})

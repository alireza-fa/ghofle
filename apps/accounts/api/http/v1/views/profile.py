from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.accounts.api.http.v1.serializers.profile import ProfileSerializer, ProfileBaseUpdateSerializer
from apps.accounts.selectors.profile import get_profile_user
from apps.api import response_code
from apps.api.response import base_response, base_response_with_error, base_response_with_validation_error

User = get_user_model()

SCHEMA_TAGS = ("Accounts",)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    @extend_schema(request=None, responses=ProfileSerializer, tags=SCHEMA_TAGS)
    def get(self, request):
        try:
            profile = get_profile_user(user=request.user)
        except User.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.USER_NOT_FOUND)

        serializer = self.serializer_class(instance=profile)

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=serializer.data)


class ProfileBaseUpdateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileBaseUpdateSerializer

    @extend_schema(request=ProfileBaseUpdateSerializer, responses=ProfileBaseUpdateSerializer, tags=SCHEMA_TAGS)
    def post(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.USER_NOT_FOUND)

        serializer = self.serializer_class(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(instance=user, validated_data=serializer.validated_data)
            return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=serializer.data)

        return base_response_with_validation_error(error=serializer.errors)

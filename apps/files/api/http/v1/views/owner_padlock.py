from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

from apps.files.api.http.v1.serializers.owner_padlock import PadlockCreateSerializer, PadlockDetailSerializer
from apps.api.response import base_response, base_response_with_error, base_response_with_validation_error
from apps.api import response_code
from apps.files.exceptions import RichPadlockLimit, PadlockDoesNotExist
from apps.files.selectors.padlock import get_user_own_padlocks
from apps.files.services.padlock import create_padlock, delete_padlock
from apps.pkg.storage.exceptions import FilePutErr


class UserOwnPadlockListView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PadlockDetailSerializer

    def get(self, request):
        padlocks = get_user_own_padlocks(user=request.user)
        serializer = self.serializer_class(instance=padlocks, many=True)
        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=serializer.data)


class CreatePadlockView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PadlockCreateSerializer
    serializer_output_class = PadlockDetailSerializer

    @extend_schema(request=PadlockCreateSerializer, responses=PadlockDetailSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                padlock = create_padlock(user=request.user, **serializer.validated_data)

                serializer = self.serializer_output_class(instance=padlock)
                return base_response(status_code=status.HTTP_201_CREATED, code=response_code.CREATED,
                                     result=serializer.data)

            except FilePutErr:
                return base_response_with_error(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                code=response_code.ERROR_UPLOAD)
            except RichPadlockLimit:
                return base_response_with_error(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                                code=response_code.PadlockLimit)

        return base_response_with_validation_error(error=serializer.errors)


class DeletePadlockView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, padlock_id):
        try:
            delete_padlock(request=request, padlock_id=padlock_id)
        except PadlockDoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PADLOCK_NOT_FOUND)

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK)

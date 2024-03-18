from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

from apps.files.api.http.v1.serializers.owner_padlock import PadlockCreateSerializer, PadlockDetailSerializer
from apps.api.response import base_response, base_response_with_error, base_response_with_validation_error
from apps.api import response_code
from apps.files.services.padlock import create_padlock
from apps.pkg.storage.exceptions import FilePutErr


class UserOwnPadlockList(APIView):
    pass


class CreatePadlock(APIView):
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
                base_response_with_error(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                         code=response_code.ERROR_UPLOAD)

        return base_response_with_validation_error(error=serializer.errors)


class UpdatePadlock(APIView):
    pass


class DeletePadlock(APIView):
    pass

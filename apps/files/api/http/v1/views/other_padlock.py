from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

from apps.api.response import base_response, base_response_with_error, base_response_with_validation_error
from apps.api import response_code
from apps.files.exceptions import PadlockDoesNotExist
from apps.files.selectors.padlock import get_padlock
from ..serializers.other_padlock import PadlockDetailSerializer


class PadlockDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PadlockDetailSerializer

    def get(self, request, padlock_id):
        try:
            padlock = get_padlock(padlock_id=padlock_id)
        except PadlockDoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PADLOCK_NOT_FOUND)

        serializer = self.serializer_class(instance=padlock, context={"request": request})
        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=serializer.data)


class PadlockOpenFileView(APIView):
    pass

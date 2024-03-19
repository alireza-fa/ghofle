from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

from apps.api.response import base_response, base_response_with_error, base_response_with_validation_error
from apps.api import response_code
from apps.api.pagination import PageNumberPagination
from apps.files.exceptions import PadlockDoesNotExist, AccessDeniedPadlockFile
from apps.files.selectors.padlock import get_padlock, get_user_buy_padlocks
from apps.files.services.padlock import open_padlock_file
from ..serializers.other_padlock import PadlockDetailSerializer


class PadlockOtherDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PadlockDetailSerializer

    @extend_schema(request=None, responses=PadlockDetailSerializer)
    def get(self, request, padlock_id):
        try:
            padlock = get_padlock(padlock_id=padlock_id)
        except PadlockDoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PADLOCK_NOT_FOUND)

        serializer = self.serializer_class(instance=padlock, context={"request": request})
        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=serializer.data)


class PadlockOpenFileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, padlock_id):
        try:
            file_url = open_padlock_file(request=request, padlock_id=padlock_id)
        except PadlockDoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PADLOCK_NOT_FOUND)
        except AccessDeniedPadlockFile:
            return base_response_with_error(status_code=status.HTTP_403_FORBIDDEN,
                                            code=response_code.OPEN_PADLOCK_FILE_LIMIT)
        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=file_url)


class UserBuyPadlockListView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PadlockDetailSerializer
    paginator = PageNumberPagination

    def get(self, request):
        padlocks = get_user_buy_padlocks(user=request.user)
        paginator = self.paginator()
        serializer = self.serializer_class(instance=paginator.paginate_queryset(queryset=padlocks, request=request),
                                           many=True, context={"request": request})
        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK,
                             result=paginator.get_paginated_response(data=serializer.data).data)

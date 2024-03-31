from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

from apps.api.response import base_response, base_response_with_error, base_response_with_validation_error
from apps.api import response_code
from apps.api.pagination import PageNumberPagination
from apps.files.exceptions import PadlockDoesNotExist, AccessDeniedPadlockFile
from apps.files.models import Padlock
from apps.files.selectors.padlock import get_padlock, get_user_buy_padlocks
from apps.files.services.padlock import open_padlock_file, padlock_buy
from apps.finance.models import Gateway
from ..serializers.other_padlock import PadlockDetailSerializer, PadlockOpenFileResponseSerializer

SCHEMA_TAGS = ("Files",)


class PadlockOtherDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PadlockDetailSerializer

    @extend_schema(request=None, responses=PadlockDetailSerializer, tags=SCHEMA_TAGS)
    def get(self, request, padlock_id):
        try:
            padlock = get_padlock(padlock_id=padlock_id)
        except Padlock.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PADLOCK_NOT_FOUND)

        serializer = self.serializer_class(instance=padlock, context={"request": request})
        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=serializer.data)


class PadlockOpenFileView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(responses=PadlockOpenFileResponseSerializer, tags=SCHEMA_TAGS)
    def get(self, request, padlock_id):
        try:
            file_url = open_padlock_file(request=request, padlock_id=padlock_id)
        except Padlock.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PADLOCK_NOT_FOUND)
        except AccessDeniedPadlockFile:
            return base_response_with_error(status_code=status.HTTP_403_FORBIDDEN,
                                            code=response_code.OPEN_PADLOCK_FILE_LIMIT)
        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=file_url)


class UserBuyPadlockListView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PadlockDetailSerializer
    paginator = PageNumberPagination

    @extend_schema(request=None, responses=PadlockDetailSerializer, tags=SCHEMA_TAGS)
    def get(self, request):
        padlocks = get_user_buy_padlocks(user=request.user)
        paginator = self.paginator()
        serializer = self.serializer_class(instance=paginator.paginate_queryset(queryset=padlocks, request=request),
                                           many=True, context={"request": request})
        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK,
                             result=paginator.get_paginated_response(data=serializer.data).data)


class PadlockBuyView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, padlock_id):
        try:
            pay_link = padlock_buy(request=request, padlock_id=padlock_id)
        except Padlock.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PADLOCK_NOT_FOUND)
        except Gateway.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.GATEWAY_NOT_FOUND)
        except Exception as err:
            return base_response_with_error(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            code=response_code.INTERNAL_SERVER_ERROR, error=str(err))

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result={"link": pay_link})

from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

from apps.api.response import base_response, base_response_with_error
from apps.api import response_code
from apps.api.pagination import PageNumberPagination
from apps.api.serializers import InternalServerErrSerializer
from apps.files.exceptions import AccessDeniedPadlockFile
from apps.files.models import Padlock, PadLockUser
from apps.files.v1.selectors.padlock import get_padlock, get_user_buy_padlocks
from apps.files.v1.serializers.owner_padlock import PadlockNotFoundErrSerializer
from apps.files.v1.services.padlock import open_padlock_file, padlock_buy
from apps.finance.v1.serializers.gateway import GatewayConnectionErrSerializer, GatewayTimeoutErrorSerializer
from apps.finance.exceptions import GatewayConnectionError, GatewayTimeoutError
from apps.finance.models import Gateway
from apps.files.v1.serializers.other_padlock import PadlockDetailSerializer, PadlockOtherDetailResponseSerializer, PadlockOpenFileSwaggerResponseSerializer, \
    OpenPadlockFileLimitErrSerializer, PadlockBuyListResponseSerializer, PadlockBuySwaggerResponseSerializer

SCHEMA_TAGS = ("Files",)


class PadlockOtherDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PadlockDetailSerializer

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(response=PadlockOtherDetailResponseSerializer),
            404: OpenApiResponse(response=PadlockNotFoundErrSerializer),
        },
        tags=SCHEMA_TAGS)
    def get(self, request, padlock_id):
        try:
            padlock = get_padlock(padlock_id=padlock_id)
        except Padlock.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PADLOCK_NOT_FOUND)

        serializer = self.serializer_class(instance=padlock, context={"request": request})
        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=serializer.data)


class PadlockOpenFileView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        responses={
            200: OpenApiResponse(response=PadlockOpenFileSwaggerResponseSerializer),
            403: OpenApiResponse(response=OpenPadlockFileLimitErrSerializer),
            404: OpenApiResponse(response=PadlockNotFoundErrSerializer),
        },
        tags=SCHEMA_TAGS)
    def get(self, request, padlock_id):
        try:
            file_url = open_padlock_file(request=request, padlock_id=padlock_id)
        except PadLockUser.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PADLOCK_NOT_FOUND)
        except AccessDeniedPadlockFile:
            return base_response_with_error(status_code=status.HTTP_403_FORBIDDEN,
                                            code=response_code.OPEN_PADLOCK_FILE_LIMIT)
        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result=file_url)


class UserBuyPadlockListView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PadlockDetailSerializer
    paginator = PageNumberPagination

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(response=PadlockBuyListResponseSerializer)
        },
        tags=SCHEMA_TAGS)
    def get(self, request):
        padlocks = get_user_buy_padlocks(user=request.user)
        paginator = self.paginator()
        serializer = self.serializer_class(instance=paginator.paginate_queryset(queryset=padlocks, request=request),
                                           many=True, context={"request": request})
        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK,
                             result=paginator.get_paginated_response(data=serializer.data).data)


class PadlockBuyView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        responses={
            200: OpenApiResponse(response=PadlockBuySwaggerResponseSerializer),
            404: OpenApiResponse(response=PadlockNotFoundErrSerializer),
            500: OpenApiResponse(response=InternalServerErrSerializer),
            503: OpenApiResponse(response=GatewayConnectionErrSerializer),
            504: OpenApiResponse(response=GatewayTimeoutErrorSerializer),
        },
        tags=SCHEMA_TAGS)
    def post(self, request, padlock_id):
        try:
            pay_link = padlock_buy(request=request, padlock_id=padlock_id)
        except Padlock.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PADLOCK_NOT_FOUND)
        except Gateway.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.GATEWAY_NOT_FOUND)
        except GatewayConnectionError:
            return base_response_with_error(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, code=response_code.GATEWAY_CONNECTION_ERROR)
        except GatewayTimeoutError:
            return base_response_with_error(status_code=status.HTTP_504_GATEWAY_TIMEOUT, code=response_code.GATEWAY_TIMEOUT_ERROR)
        except Exception as err:
            return base_response_with_error(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            code=response_code.INTERNAL_SERVER_ERROR, error=str(err))

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK, result={"link": pay_link})

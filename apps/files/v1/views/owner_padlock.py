from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiResponse, OpenApiExample
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

from apps.api.pagination import PageNumberPagination
from apps.api.swagger_fields import PADLOCK_THUMBNAIL_DESCRIPTION, PADLOCK_CREATE_EXAMPLE_VALUE, \
    PADLOCK_FILE_DESCRIPTION, PADLOCK_REVIEW_DESCRIPTION, PADLOCK_PRICE_DESCRIPTION
from apps.files.v1.serializers.owner_padlock import PadlockCreateSerializer, PadlockDetailSerializer, \
    PadlockResponseSerializer, CreatePadlockResponseSerializer, FilePutErrorSerializer, RichPadlockLimitErrSerializer, \
    CreatePadlockBadRequestSerializer, DeletePadlockResponseSerializer, PadlockNotFoundErrSerializer
from apps.api.response import base_response, base_response_with_error, base_response_with_validation_error
from apps.api import response_code
from apps.files.exceptions import RichPadlockLimit
from apps.files.models import Padlock
from apps.files.v1.selectors.padlock import get_user_own_padlocks
from apps.files.v1.services.padlock import create_padlock, delete_padlock
from pkg.storage.exceptions import FilePutErr

SCHEMA_TAGS = ("Files",)


class UserOwnPadlockListView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PadlockDetailSerializer
    paginator = PageNumberPagination

    @extend_schema(
        request=OpenApiRequest(request=None),
        responses={
            200: OpenApiResponse(response=PadlockResponseSerializer)
        },
        tags=SCHEMA_TAGS)
    def get(self, request):
        padlocks = get_user_own_padlocks(user=request.user)
        paginator = self.paginator()
        serializer = self.serializer_class(
            instance=paginator.paginate_queryset(queryset=padlocks, request=request), many=True)
        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK,
                             result=paginator.get_paginated_response(data=serializer.data).data)


class CreatePadlockView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PadlockCreateSerializer
    serializer_output_class = PadlockDetailSerializer

    @extend_schema(
        request=OpenApiRequest(request=PadlockCreateSerializer, examples=[
            OpenApiExample(name="thumbnail", value=PADLOCK_CREATE_EXAMPLE_VALUE, description=PADLOCK_THUMBNAIL_DESCRIPTION),
            OpenApiExample(name="file", value=PADLOCK_CREATE_EXAMPLE_VALUE, description=PADLOCK_FILE_DESCRIPTION),
            OpenApiExample(name="review_active", value=PADLOCK_CREATE_EXAMPLE_VALUE, description=PADLOCK_REVIEW_DESCRIPTION),
            OpenApiExample(name="price", value=PADLOCK_CREATE_EXAMPLE_VALUE, description=PADLOCK_PRICE_DESCRIPTION)
        ]),
        responses={
            200: OpenApiResponse(response=CreatePadlockResponseSerializer),
            401: OpenApiResponse(response=CreatePadlockBadRequestSerializer),
            500: OpenApiResponse(response=FilePutErrorSerializer),
            406: OpenApiResponse(response=RichPadlockLimitErrSerializer),
        },
        tags=SCHEMA_TAGS)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                padlock = create_padlock(request=request, **serializer.validated_data)
            except FilePutErr:
                return base_response_with_error(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                code=response_code.ERROR_UPLOAD)
            except RichPadlockLimit:
                return base_response_with_error(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                                code=response_code.PadlockLimit)

            serializer = self.serializer_output_class(instance=padlock)
            return base_response(status_code=status.HTTP_201_CREATED, code=response_code.CREATED,
                                 result=serializer.data)

        return base_response_with_validation_error(error=serializer.errors)


class DeletePadlockView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        responses={
            200: OpenApiResponse(response=DeletePadlockResponseSerializer),
            404: OpenApiResponse(response=PadlockNotFoundErrSerializer),
        },
        tags=SCHEMA_TAGS)
    def get(self, request, padlock_id):
        try:
            delete_padlock(request=request, padlock_id=padlock_id)
        except Padlock.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PADLOCK_NOT_FOUND)

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK)

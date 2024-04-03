from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

from apps.api import response_code
from apps.api.response import base_response_with_error, base_response
from apps.api.serializers import InternalServerErrSerializer
from apps.finance.gateways.zibal.exceptions import StatusErr
from apps.finance.models import Payment
from apps.finance.v1.serializers.gateway import GatewayTimeoutErrorSerializer, GatewayConnectionErrSerializer
from apps.finance.v1.serializers.payment import PaymentNotFoundErrSerializer, PaymentVerifyResponseSerializer, \
    PaymentStatusErrSerializer
from apps.finance.v1.services.payment import verify_payment

SCHEMA_TAGS = ("Finance",)


class VerifyPayView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        responses={
            200: OpenApiResponse(response=PaymentVerifyResponseSerializer),
            404: OpenApiResponse(response=PaymentNotFoundErrSerializer),
            406: OpenApiResponse(response=PaymentStatusErrSerializer),
            500: OpenApiResponse(response=InternalServerErrSerializer),
            503: OpenApiResponse(response=GatewayConnectionErrSerializer),
            504: OpenApiResponse(response=GatewayTimeoutErrorSerializer),
        },
        tags=SCHEMA_TAGS)
    def get(self, request, track_id):
        try:
            verify_payment(request=request, track_id=track_id)
        except Payment.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PAYMENT_NOT_FOUND)
        except StatusErr as err:
            return base_response_with_error(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                            code=response_code.INVALID_PAYMENT, error=str(err))
        except ConnectionError:
            return base_response_with_error(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, code=response_code.GATEWAY_CONNECTION_ERROR)
        except TimeoutError:
            return base_response_with_error(status_code=status.HTTP_504_GATEWAY_TIMEOUT, code=response_code.GATEWAY_TIMEOUT_ERROR)
        except Exception as err:
            return base_response_with_error(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            code=response_code.INTERNAL_SERVER_ERROR, error=str(err))

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK)

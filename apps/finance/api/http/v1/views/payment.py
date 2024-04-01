from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

from apps.api import response_code
from apps.api.response import base_response_with_error, base_response
from apps.finance.gateways.zibal.exceptions import StatusErr
from apps.finance.models import Payment
from apps.finance.services.payment import verify_payment

SCHEMA_TAGS = ("Finance",)


class VerifyPayView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(responses=None, tags=SCHEMA_TAGS)
    def get(self, request, track_id):
        try:
            verify_payment(request=request, track_id=track_id)
        except Payment.DoesNotExist:
            return base_response_with_error(status_code=status.HTTP_404_NOT_FOUND, code=response_code.PAYMENT_NOT_FOUND)
        except StatusErr as err:
            return base_response_with_error(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                            code=response_code.INVALID_PAYMENT, error=str(err))
        except Exception as err:
            return base_response_with_error(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            code=response_code.INTERNAL_SERVER_ERROR, error=str(err))

        return base_response(status_code=status.HTTP_200_OK, code=response_code.OK)

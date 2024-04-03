from typing import Dict

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpRequest

from apps.finance.gateways.zibal.zibal import send_request, verify, RESULT_100, RESULT_201
from apps.finance.models import Gateway, Payment
from apps.utils import client

User = get_user_model()


def create_payment(gateway_name: int, user: User, payment_type: int,
                   amount: int, description: str, commit=False) -> Payment:
    gateway = Gateway.objects.get(name=gateway_name)

    payment = Payment(gateway=gateway, user=user, payment_type=payment_type,
                      amount=amount, description=description)

    if commit:
        payment.save()

    return payment


def get_pay_function(gateway_name):
    gateway_functions = {
        Gateway.ZIBAL: {
            "request": send_request,
            "verify": verify,
        }
    }
    return gateway_functions[gateway_name]


def get_payment_request(payment: Payment) -> Dict:
    gateway_function = get_pay_function(payment.gateway.name)

    request_to_gateway_data = gateway_function["request"](
        payment.gateway.authorization, amount=payment.amount,
        callback_url=payment.gateway.callback_url, description=payment.description,
        mobile=payment.user.phone_number)

    return request_to_gateway_data


def update_payment_verify(payment: Payment, verify_payment_data: Dict, client_info: Dict):
    with transaction.atomic():
        payment.status = True
        payment.ref_number = verify_payment_data["refNumber"]
        payment.paid_at = verify_payment_data["paidAt"]
        payment.card_number = verify_payment_data["cardNumber"]
        payment.ip_address = client_info[client.IP_ADDRESS]
        payment.device_name = client_info[client.DEVICE_NAME]
        payment.save()


def verify_payment(request: HttpRequest, track_id: int) -> dict:
    user = request.user

    payment = Payment.objects.get(track_id=track_id, user=user)

    gateway_function = get_pay_function(payment.gateway.name)

    verify_payment_data = gateway_function["verify"](merchant=payment.gateway.authorization, track_id=payment.track_id)

    client_info = client.get_client_info(request=request)

    if verify_payment_data["result"] == RESULT_100:
        update_payment_verify(payment=payment, verify_payment_data=verify_payment_data, client_info=client_info)
    elif verify_payment_data["result"] == RESULT_201:
        if not payment.status:
            update_payment_verify(payment=payment, verify_payment_data=verify_payment_data, client_info=client_info)

    return verify_payment_data

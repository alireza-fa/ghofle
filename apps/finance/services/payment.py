from django.contrib.auth import get_user_model

from apps.finance.gateways.zibal.zibal import send_request
from apps.finance.models import Gateway, Payment

User = get_user_model()


def create_payment(gateway_name: int, user: User, payment_type: int,
                   amount: int, description: str) -> Payment:
    gateway = Gateway.objects.get(name=gateway_name)

    payment = Payment.objects.create(gateway=gateway, user=user, payment_type=payment_type,
                                     amount=amount, description=description)

    return payment


def get_payment_pay_link(payment: Payment):

    request_to_gateway_data = send_request(payment.gateway.authorization, amount=payment.amount,
                                           callback_url=payment.gateway.callback_url, description=payment.description,
                                           mobile=payment.user.phone_number)

    return request_to_gateway_data["link"]

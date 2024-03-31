from typing import Dict
import json
import requests

from apps.finance.gateways.zibal.exceptions import StatusErr

"""
document link:
            https://help.zibal.ir/IPG/API/
"""

RESULT_100 = "verify"
RESULT_102 = "Not found merchant"
RESULT_103 = "Inactive merchant"
RESULT_104 = "Invalid merchant"
RESULT_105 = "Amount most be grater than 1_000 rial"
RESULT_106 = "Invalid callback url(start with http or https"
RESULT_113 = "Amount is greater than maximum"
RESULT_201 = "Already paid"
RESULT_202 = "The order has not been paid or failed"
RESULT_203 = "Invalid trackId"

RESULTS = {
    102: RESULT_102,
    103: RESULT_103,
    104: RESULT_104,
    105: RESULT_105,
    106: RESULT_106,
    113: RESULT_113,
    201: RESULT_201,
    202: RESULT_202,
    203: RESULT_203
}


request_url = "https://gateway.zibal.ir/v1/request"
pay_url = "https://gateway.zibal.ir/start/{}"
verify_url = "https://gateway.zibal.ir/v1/verify"


def get_pay_url(track_id: int) -> str:
    return pay_url.format(track_id)


def send_request(merchant: str, amount: int, callback_url: str, description: str,
                 order_id: str | None = None, mobile: str | None = None, allowed_cards: str | None = None,
                 ledger_id: str | None = None, link_to_pay: bool = False, sms: bool = False) -> Dict:
    """
    :return: response body:
                trackId: int
                result: int(100, 102, 103, 104, 106, 113)
                payLink: str
                message: str
    """
    body = {
        "merchant": merchant,
        "amount": amount,
        "callbackUrl": callback_url,
        "description": description,
        "orderId": order_id,
        "mobile": mobile,
        "allowedCards": allowed_cards,
        "ledgerId": ledger_id,
        "linkToPay": link_to_pay,
        "sms": sms,
    }

    try:
        response = requests.post(request_url, json=body)
        if response.status_code != 200:
            raise ConnectionError()

        response_body = json.loads(response.text)

        if response_body["result"] == 100:
            response_body["link"] = get_pay_url(response_body["trackId"])
            return response_body

        raise StatusErr(RESULTS[response_body["result"]])

    except TimeoutError as err:
        raise TimeoutError(err)
    except ConnectionError as err:
        raise ConnectionError(err)


def callback(merchant: str, success: int, track_id: int, order_id: str, status: int):
    """
    :param merchant: authorization key
    :param success: 1 for success and 0 for failure
    :param track_id: for checkout
    :param order_id: order id(for example order.id)
    :param status: pay situation
    example a callback: https://yourcallbackurl.com/callback?trackId=9900&success=1&status=2&orderId=1
    :return:
    """
    if success == 0 or status != 1:
        raise ValueError
    verify(merchant=merchant, track_id=track_id)


def verify(merchant: str, track_id: int) -> Dict:
    """
    :param merchant: authorization key
    :param track_id: for checkout
    :return: {
                paidA
                cardNumber(mask)
                status
                amount
                refNumber
                description
                orderId
                result
                message
              }
    """
    body = {
        "merchant": merchant,
        "trackId": track_id
    }

    try:
        response = requests.post(request_url, json=body)
        if response.status_code != 200:
            raise ConnectionError()

        response_body = json.loads(response.text)

        if response_body["result"] == 100:
            return response_body

        raise StatusErr(RESULTS[response_body["result"]])

    except TimeoutError as err:
        raise TimeoutError(err)
    except ConnectionError as err:
        raise ConnectionError(err)

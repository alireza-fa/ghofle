from typing import Dict
import json
import requests

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

RESULTS = {
    102: RESULT_102,
    103: RESULT_103,
    104: RESULT_104,
    105: RESULT_105,
    106: RESULT_106,
    113: RESULT_113,
}


request_url = "https://gateway.zibal.ir/v1/request"
pay_url = "https://gateway.zibal.ir/start/{}"


def send_request(merchant: str, amount: int, callback_url: str, description: str,
                 order_id: str, mobile: str, allowed_cards: str, ledger_id: str,
                 link_to_pay: bool, sms: bool) -> Dict:
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

        if response_body["result"] == 200:
            return response_body

        raise ValueError(RESULTS[response_body["result"]])

    except TimeoutError as err:
        raise TimeoutError(err)
    except ConnectionError as err:
        raise ConnectionError(err)


def get_pay_url(track_id: int) -> str:
    return pay_url.format(track_id)

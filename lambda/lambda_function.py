import os
import json
from http.client import HTTPConnection


ENDPOINT = ""
MACAROON = ""
HEADERS = { 'macaroon': MACAROON }


def _request_lightning(transaction_label):
    conn = HTTPConnection(ENDPOINT)
    status = None

    try:
        print("connecting to waitInvoice route")
        conn.request('GET', f"/v1/invoice/waitInvoice/{transaction_label}", headers=HEADERS)
        response = conn.getresponse()

        status_code = response.status
        status = status_code == 200

        if not status:
            print("connecting to listInvoices route")
            conn.request('GET', f"/v1/invoice/listInvoices?label={transaction_label}", headers=HEADERS)
            response = conn.getresponse()

            if response.status == 200:
                content = json.loads(response.read().decode('utf-8'))
                invoices = content.get("invoices", [])

                status = len(invoices) and invoices[0].get("status") == "paid"

    except Exception as e:
        print('An error occurred:', e)
    finally:
        conn.close()
    print("returning status")
    return "settled" if status else "expired"

def request_handler(transaction_label, callback_urls):
    status = _request_lightning(transaction_label)

    for host, path in callback_urls:
        print("calling callback url")
        conn = HTTPConnection(host)
        conn.request('GET', f"{path}?transaction_label={transaction_label}&status={status}")
        print("called callback url")
        conn.close()

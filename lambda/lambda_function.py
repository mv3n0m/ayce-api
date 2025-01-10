import os
import json
from http.client import HTTPConnection


ENDPOINT = "18.141.234.127"
MACAROON = "AgELYy1saWdodG5pbmcCPlN1biBBdWcgMTMgMjAyMyAxMDozMjozNiBHTVQrMDAwMCAoQ29vcmRpbmF0ZWQgVW5pdmVyc2FsIFRpbWUpAAAGIFEMJRQf93S+lhlnJqsqLJHEPNdrPL0eKwDOA9Xp9p6m"
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

request_handler("", "")

# def r1equest_handler(transaction_label, amount, *args, **kwargs):
#     mid, tid = transaction_label.split("_")
#     status = "expired"

#     db_query = {"_id": ObjectId(mid)}

#     merchant = db.get("merchants", db_query)[0]
#     # It is possible that either btc or usd gets filled first, so ...<next comment on balance update>
#     balances = merchant.get("balances", {"usd": 0, "btc": 0})

#     try:
#         url = f"{ENDPOINT}/v1/invoice/waitInvoice/{transaction_label}"
#         response = requests.get(url, headers={"macaroon": MACAROON})

#         # update balance only when the transaction was in pending state or not settled previously
#         if response.status_code == 200:
#             status = "settled"
#             # ... this might fail is usd value was present already and vice-versa (when implemented for usd)
#             balances["btc"] += amount
#     except:
#         status = "failed"

#     # if status != "settled":
#     #     url = f"{ENDPOINT}/v1/invoice/listInvoices?label={transaction_label}"
#     #     response = requests.get(url, headers={"macaroon": MACAROON})

#     #     if response.status_code == 200:
#     #         content = json.loads(response.content)
#     #         invoices = content.get("invoices", [])

#     #         if len(invoices) and invoices[0].get("status") == "paid":
#     #             status = "settled"
#     #             # ... this might fail is usd value was present already and vice-versa (when implemented for usd)
#     #             balances["btc"] += amount

#     db.update("transactions", {"transaction_label": transaction_label}, {"status": status})
#     db.update("merchants", db_query, {"balances": balances})


# def test_func():
#     transaction_label = "64d937628cd8aa10ef9cc4b8_1692213619"

#     url = f"{ENDPOINT}/v1/invoice/listInvoices?label={transaction_label}"
#     response = requests.get(url, headers={"macaroon": MACAROON})




# test_func()
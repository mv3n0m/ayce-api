import requests
from datetime import datetime, timedelta


class Tokenize:

    def __init__(self, config):
        self.headers = {'X-TKX-TOKEN': config.get("secret_key")}
        self.uri = config.get("uri")

    def _request(self, path, payload=None, method="GET"):
        headers = self.headers
        if method == "GET":
            request = requests.get
            body = {"params": payload}
        else:
            request = requests.post
            headers["Content-Type"] = "application/json"
            body = {"json": payload}

        kwargs = {"url": self.uri + path, "headers": headers, **body}

        response = request(**kwargs)
        if response.status_code != 200:
            print(response.json())
            return {"error": "Unable to get response."}

        body = response.json()
        data = body.get("data")
        if not data:
            print(body)
            return {"error": "Data not available."}

        return data

    def get_price(self, base="BTC", quote="USD"):
        response = self._request("/market/get-last-market-price", {"market": f"{quote}-{base}"})

        if "error" not in response:
            response = {"price": response.get("lastPrice")}

        return response

    def buy(self, units, base="BTC", quote="USD"):
        response = self._request("/order", {"market": f"{quote}-{base}", "side": "buy", "units": units, "orderType": "market"}, "POST")
        return response

    def sell(self, units, base="BTC", quote="USD"):
        response = self._request("/order", {"market": f"{quote}-{base}", "side": "sell", "units": units, "orderType": "market"}, "POST")
        return response

    def get_orders(self, status="pending", base="BTC", quote="USD", limit=5):
        response = self._request("/order", {"market": f"{quote}-{base}", "limit": limit})
        return response

    def get_balances(self):
        response = self._request("/account/balances")
        return response

    def get_balance(self, currency):
        response = self._request("/account/balance", {"currency": currency})

        if "error" not in response:
            response = {"balance": response.get("balance")}

        return response

    def get_exchange_values(self, amount, _from, _to, surrcharge_rate=0.00604):
        _from = _from.lower()
        _to = _to.lower()

        response = self.get_price()
        if response.get("error"):
            return response

        quote_price = float(response.get("price"))
        surrcharge = quote_price * surrcharge_rate

        if _from == "btc":
            conversion_rate = quote_price - surrcharge
            quote_amount = amount * conversion_rate
            transfer_fee = f"{round(amount * surrcharge_rate, 8):.8f} BTC"
            required_amount = amount * (1 + surrcharge_rate)

        elif _from == "usd":
            conversion_rate = quote_price + surrcharge
            quote_amount = amount / conversion_rate
            transfer_fee = amount / surrcharge
            required_amount = amount + transfer_fee
            transfer_fee = f"{round(transfer_fee, 4)} USD"

        response = {
            "_from": { "currency": _from, "amount": amount },
            "_to": { "currency": _to, "amount": quote_amount },
            "conversion_rate": f"${conversion_rate} BTC/USD",
            "transfer_fee": transfer_fee,
            "required_amount": required_amount
        }

        for i in ["_from", "_to"]:
            key = f"{response[i]['currency'].lower()}_amount"
            response[key] = response[i]["amount"]

        return response


    def exchange(self, amount, _from, _to):
        _from = _from.lower()
        _to = _to.lower()

        if _from == "btc":
            m = self.sell
        elif _from == "usd":
            m = self.buy

        response = m(amount)
        return response
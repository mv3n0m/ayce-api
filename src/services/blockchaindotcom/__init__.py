import time
import logging
import requests
from datetime import datetime, timedelta

class BtcApi:

    def __init__(self, rst):
        self.base_url = "https://blockchain.info"
        self.rst = rst

    def __convert(self):
        url = f"{self.base_url}/tobtc"
        params = { "currency": "USD", "value": 100000 }
        response = requests.get(url, params=params)

        if response.status_code != 200:
            logging.info(f"BlockchainDotCom <amount: {amount} | currency: {currency}> - ERROR_CODE: {response.status_code}")
            conversion_rate = self.rst._get("conversion_rate")

        return response.json()

    def convert(self, amount=None, currency=None, forced=False):
        conversion_rate = None
        if not forced:
            try:
                conversion_expiry = self.rst._get("conversion_expiry")
                if "error" not in conversion_expiry:
                    if datetime.now().timestamp() <= float(conversion_expiry):
                        conversion_rate = float(self.rst._get("conversion_rate"))
            except:
                pass

        if not conversion_rate:
            conversion_rate = self.__convert()
            self.rst._set("conversion_rate", conversion_rate)
            self.rst._set("conversion_expiry", (datetime.now() + timedelta(minutes=3)).timestamp())

        btc_price = 100000 / conversion_rate

        if not amount:
            response = [['1', "BTC"], [str(round(btc_price, 4)), "USD"]]

        if currency.lower() == "usd":
            response = [[str(amount), "USD"], [f"{round((amount * conversion_rate / 100000), 8):.8f}", "BTC"]]

        if currency.lower() == "btc":
            response = [[str(amount), "BTC"], [f"{round(amount * btc_price, 4)}", "USD"]]

        return { i: { k: l for k, l in zip(["amount", "currency"], j) } for i, j in zip(["_from", "_to"], response) }
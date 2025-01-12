import os
from .utils import RPCHandler, RequestHandler


class OnChain(RPCHandler):

    def __init__(self, config):
        auth = config.pop("username"), config.pop("password")
        config["auth"] = auth
        self.default_wallet = os.environ.get("BTC_ONCHAIN_DEFAULT_WALLET")
        super().__init__(config)

    def create_wallet(self, wallet_name):
        return self._request("createwallet", [wallet_name])

    def create_payment_address(self, wallet_name=None, *args, **kwargs):
        return self._request("getnewaddress", path=f"/wallet/{wallet_name or self.default_wallet}")

    def create_new_address(self, wallet_name=None):
        return self._request("getnewaddress", path=f"/wallet/{wallet_name or self.default_wallet}")

    def get_wallet_balance(self, wallet_name=None):
        return self._request("getbalance", path=f"/wallet/{wallet_name or self.default_wallet}")

    def get_address_balance(self, address):
        return self._request("getbalance", path=f"/address/{address}")

    def send(self, amount, address, wallet_name=None):
        return self._request("sendtoaddress", [address, amount], path=f"/wallet/{wallet_name or self.default_wallet}")


class Lightning(RequestHandler):

    def __init__(self, config):
        super().__init__(config)

    def create_wallet(self, wallet_name):
        return ""

    def create_payment_address(self, amount, label, description="Ayce POS transaction"):
        payload = {
            "amount": int(amount * (10 ** 11)),
            "label": label,
            "description": description,
            "expiry": 6000
        }

        response = self._request("/v1/invoice/genInvoice", method="POST", payload=payload)
        status_code, _ = response

        return response

    def create_new_address(self, wallet_name):
         return self._request("/v1/newaddr")

    def get_wallet_balance(self, wallet_name):
        return ""

    def get_address_balance(self, address):
        return ""


_chains = {
    "on-chain": OnChain,
    "lightning": Lightning
}
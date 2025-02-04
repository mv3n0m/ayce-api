import os
import logging
from .chains import _chains


def get_payment_address(node, payload, counter=0):
        status_code, content = node.create_payment_address(**payload)

        if status_code not in [200, 201]:
            if counter == 2:
                return content
            counter += 1
            logging.info(f"Retry # {counter}")
            content = get_payment_address(node, payload, counter)

        return content


class BTCNode:

    def __init__(self, config):
        self.nodes = {}

        for k, v in _chains.items():
            conf = config.get(k)

            if not conf:
                raise Exception("Invalid/unavailable node")

            self.nodes[k] = v(conf)

    def get_node(self, mode):
        return self.nodes[mode]

    def get_payment_addresses(self, payload, modes=None):
        if not modes:
            modes = self.nodes.keys()

        results = {}
        for k, v in self.nodes.items():
            if k not in modes:
                continue

            response = get_payment_address(v, payload)
            if response.get("error"):
                print(response)
                return response

            results[k] = response.get("result")
            expiry = response.get("expiry")
            if expiry:
                results["expiry"] = expiry

        return results

    def transfer(self, *args, **kwargs):
        return self.nodes["on-chain"].send(*args, **kwargs)
    
    def get_balance(self):
        _balance = self.nodes["on-chain"].get_wallet_balance()[1]["result"]

        return _balance
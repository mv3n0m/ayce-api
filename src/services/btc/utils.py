import os
import json
import logging
import requests

headers = {'Content-Type': 'text/plain'}

class RPCHandler:

    def __init__(self, config):
        for key, value in config.items():
            setattr(self, key, value)

    def _request(self, method, params=[], path=""):
        payload = {
            "jsonrpc": "1.0",
            "id": "demo",
            "method": method,
            "params": params
        }
        payload = json.dumps(payload).encode()
        response = requests.post(self.uri + path, data=payload, headers=headers, auth=self.auth)

        logging.info(response.content)
        content = json.loads(response.content.decode())

        return (response.status_code, content)


class RequestHandler:

    def __init__(self, config):
        for key, value in config.items():
            setattr(self, key, value)

    def _request(self, path="", method="GET", payload=None):
        request = requests.post if method == "POST" else requests.get

        response = request(self.uri + path, headers={"macaroon": self.macaroon, "Content-Type": "application/json"}, json=payload)
        content = json.loads(response.content.decode())

        logging.info(content)

        # expiry must be checked properly here as well as on lambda as it is expiring even after payment (maybe last moment update)
        return (response.status_code, {"result": content.get("address") or content.get("bolt11"), "expiry": content.get("expires_at")})

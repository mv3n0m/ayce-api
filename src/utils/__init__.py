import jwt
import random
from uuid import uuid4
from flask import make_response, jsonify
from datetime import datetime, timedelta
from src.settings import JWT_EXPIRY_DAYS, APP_SECRET


def responsify(response, status_code=None):

    if not status_code:
        status_code = 400 if isinstance(response, dict) and "error" in response else 200

    if isinstance(response, dict):
        return make_response(jsonify(response), status_code)
    return make_response(jsonify({"data": response}))


def decode_access_token(token):
    return jwt.decode(token, APP_SECRET, "HS256")

def create_access_token(payload):
    payload["exp"] = (datetime.now() + timedelta(days=JWT_EXPIRY_DAYS)).timestamp()
    return jwt.encode(payload, APP_SECRET, "HS256")


def get_token():
    return str(uuid4())

def get_otp():
    return str(random.randint(100000, 999999))

def get_token_otp_pair():
    return get_token(), get_otp()
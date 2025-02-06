import jwt
from flask import request
from datetime import datetime
from src.settings import rst
from src.routes.handlers.user import User
from src.utils import responsify, decode_access_token


def handle_jwt(require_user=False):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        return {"error": "JWT Token not provided."}, 400

    try:
        token = bearer_token.split("Bearer ")[1]
        payload = decode_access_token(token)
    except Exception as e:  # pylint: disable=bare-except
        print(e)
        return {"error": "Invalid JWT token."}, 400

    if payload.get("exp") < datetime.now().timestamp():
        return {"error": "JWT token expired."}, 403

    user_id = payload.get("_pk")
    _user = 'None'

    try:
        _user = rst._get(user_id)
    except Exception as e:
        print(e)

    if _user == 'None' or require_user:
        try:
            user = User.from_id(user_id)
            status = 'active' if user.active == 1 else 'inactive'
        except Exception as e:
            print(e)
            return {"error": "JWT Token not associated with any user."}, 401

        # rst._set(user_id, status)
        _user = status

    if _user != 'active':
        return {"error": "User inactive."}, 401

    _kwargs = {}
    try:
        if request.method == "GET":
            _kwargs = request.args
        else:
            _kwargs = request.json
    except Exception as e:
        print(e)

    return _kwargs, user if require_user else user_id
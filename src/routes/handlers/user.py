import jwt
import logging
from .base import Base
from uuid import uuid4
from datetime import datetime
from src.settings import mailer, rst
from src.utils import create_access_token
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash


class User(Base):
    collection = "users"

    @classmethod
    def register(cls, email, password, username="", account_type="business"):
        email = email.lower()
        account_type = account_type.lower()
        password = generate_password_hash(password, "scrypt")

        _user = {
            "username": username,
            "email": email,
            "password": password,
            "account_type": account_type,
            "created_at": int(datetime.now().timestamp()),
            "active": 0
        }

        try:
            _user = super().create(_user)
        except DuplicateKeyError as e:
            err_msg = f"User with email: {email} already exists."
            # Maybe later on create a logger class for proper flexibility and options
            # Or maybe use the logging library itself for proper validation
            logging.info(f"{e.__class__.__name__} -> {err_msg}\n\t{e.details['errmsg']}")
            return {"error": err_msg}, 400
        except Exception as e:
            logging.info(f"{e}")
            return {"error": "Unable to create user."}, 500

        user_id = _user._pk
        token = str(uuid4())

        try:
            data = {
                "mail_type": "email verification",
                "name": username or "User",
                "email": email,
                "payload": {
                    "token": token,
                    "company_name": "Ayce Express",
                    "contact_information": "",
                }
            }
            mailer.send(data)
        except Exception as e:
            print(e)
            return {"error": "Failed to send verification email."}, 500

        rst._set(token, user_id)

        return {"success": "Verification link sent to the user's email address."}, 201


    @classmethod
    def verify(cls, token):
        try:
            value = rst._get(token)
        except Exception as e:
            return {"error": e.__str__()}, 400

        if not value or value == 'None':
            return {"error": "Invalid token."}, 400

        try:
            _user = super()._from_query({"_id": value})
        except ValueError as e:
            logging.info(f"{e}")
            return {"error": "User doesn't exist."}, 404
        except Exception as e:
            logging.info(f"{e}")
            return {"error": "Unable to fetch user."}, 500

        if _user.active:
            logging.info(f"User already verified. - {value}: {token}")
            return {"error": "Invalid token."}, 400

        _user.push({"active": 1, "balances": {"usd": 0, "btc": 0}})

        return {"success": "User verification successful."}, 200


    @classmethod
    def login(cls, email, password, account_type="business"):
        email = email.lower()
        account_type = account_type.lower()
        # Later on maybe need to work on account_type for same user/email
        try:
            _user = super()._from_query({"email": email})
        except ValueError as e:
            logging.info(f"{e}")
            return {"error": "User doesn't exist."}, 404
        except Exception as e:
            logging.info(f"{e}")
            return {"error": "Unable to fetch user."}, 500

        if account_type == "admin" and  _user.account_type != "admin":
            return {"error": "Unauthorized"}, 401

        # setting password must occur after verification email
        # So this will be checked after verfified status below
        if not check_password_hash(_user.password, password):
            return {"error": "Incorrect password."}, 400

        if _user.account_type != account_type:
            return {"error": f"Not a {account_type} account."}, 400

        if _user.active == 0:
            return {"error": "User not verified."}, 403

        if _user.active == -1:
            return {"error": "Inactive user."}, 403

        payload = {"_pk": _user._pk, "account_type": account_type}
        access_token = create_access_token(payload)
        # store and get secret key as env variables
        # as well as frontend url store as environment variable

        return {"success": "Login successful.", "access_token": access_token, "account_type": account_type}, 200


    @classmethod
    def reset_request(cls, email):
        email = email.lower()

        try:
            _user = super()._from_query({"email": email})
        except ValueError as e:
            logging.info(f"{e}")
            return {"error": "User doesn't exist."}, 404
        except Exception as e:
            logging.info(f"{e}")
            return {"error": "Unable to fetch user."}, 500

        if _user.active == 0:
            return {"error": "User not verified"}, 403

        if _user.active == -1:
            return {"error": "Inactive user."}, 403

        user_id = _user._pk
        token = str(uuid4())

        try:
            data = {
                "mail_type": "password reset",
                "name": _user.username or "User",
                "email": email,
                "payload": {
                    "token": token,
                    "company_name": "Ayce Express",
                    "contact_information": "",
                }
            }
            mailer.send(data)
        except Exception as e:
            print(e)
            return {"error": "Failed to send reset email."}, 500

        rst._set(token, user_id)

        return {"success": "Reset link sent to the user's email address."}, 200


    @classmethod
    def reset_confirm(cls, token, password):
        try:
            value = rst._get(token)
        except Exception as e:
            return {"error": e.__str__()}, 400

        if not value or value == 'None':
            return {"error": "Invalid token."}, 400

        rst._del(token)

        try:
            _user = super()._from_query({"_id": value})
        except ValueError as e:
            logging.info(f"{e}")
            return {"error": "User doesn't exist."}, 404
        except Exception as e:
            logging.info(f"{e}")
            return {"error": "Unable to fetch user."}, 500

        if check_password_hash(_user.password, password):
            return {"error": "Password cannot be set to the previous one."}, 400

        _user.push({"password": generate_password_hash(password, "scrypt")})

        return {"success": "Password updation successful."}, 200


    @classmethod
    def change_password(cls, user_id, password):
        try:
            _user = super()._from_query({"_id": user_id})
        except ValueError as e:
            logging.info(f"{e}")
            return {"error": "User doesn't exist."}, 404
        except Exception as e:
            logging.info(f"{e}")
            return {"error": "Unable to fetch user."}, 500

        if check_password_hash(_user.password, password):
            return {"error": "Password cannot be set to the previous one."}, 400

        _user.push({"password": generate_password_hash(password, "scrypt")})

        return {"success": "Password updation successful."}, 200


    def get_balance(self, _key=None):
        if not _key:
            return self.balances

        return self.balances[_key]


    def update_balance(self, _key=None, _value=None, obj=None):
        if _key and _value:
            self.balances[_key] += _value
        elif obj:
            for k, v in obj.items():
                self.balances[k] += v
        else:
            return

        self.push({"balances": self.balances})

    @classmethod
    def from_email(cls, email):
        return super()._from_query({"email": email})

    @classmethod
    def from_ayce_id(cls, ayce_id):
        return super()._from_query({"ayce_id": ayce_id})


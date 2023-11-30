from .handlers.user import User
from .handlers import create_blueprint
from src.utils import responsify
from src.utils.args_schema import token_args, auth_args, email_args, password_args


bp, route = create_blueprint("users", __name__, "/users")


@route("/register", ["POST"], auth_args, _auth=None)
def register(*args, **kwargs):
  return responsify(*User.register(**kwargs))

@route("/verify", ["POST"], token_args(), _auth=None)
def verify(*args, **kwargs):
  return responsify(*User.verify(**kwargs))

@route("/login", ["POST"], auth_args, _auth=None)
def login(*args, **kwargs):
  return responsify(*User.login(**kwargs))

@route("/request-password-reset", ["POST"], email_args, _auth=None)
def request_password_reset(*args, **kwargs):
  return responsify(*User.reset_request(**kwargs))

@route("/reset-password", ["POST"], {**token_args(), **password_args}, _auth=None)
def reset_password(*args, **kwargs):
  return responsify(*User.reset_confirm(**kwargs))

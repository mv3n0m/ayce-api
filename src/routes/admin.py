from .handlers import create_blueprint
from .handlers.user import User
from src.utils import responsify
from src.utils.args_schema import token_args, auth_args, email_args, password_args


bp, route = create_blueprint("admin", __name__, "/admin")

@route('/login', ["POST"], auth_args, _auth=None)
def admin_login(*args, **kwargs):
    account_type = kwargs.get("account_type")
    if (account_type and account_type != "admin"):
        return responsify({"error": "Invalid account_type"}, )
    return responsify(*User.login(account_type="admin", **kwargs))

@route('/stats', _identity=True)
def stats(_user):
    print('user', _user)
    return responsify({'test': 1})
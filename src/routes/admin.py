from .handlers import create_blueprint
from .handlers.user import User
from src.utils import responsify
from src.utils.args_schema import token_args, auth_args, email_args, password_args
from src.settings import mdb, btcdc
from datetime import datetime, timedelta

bp, route = create_blueprint("admin", __name__, "/admin")

@route('/login', ["POST"], auth_args, _auth=None)
def admin_login(*args, **kwargs):
    account_type = kwargs.get("account_type")
    if (account_type and account_type != "admin"):
        return responsify({"error": "Invalid account_type"}, )
    return responsify(*User.login(account_type="admin", **kwargs))

@route('/stats', _identity=True)
def stats(_user):

    if (_user.account_type != "admin"):
        return responsify({"error": "Unauthorized"}, 401)

    one_year_ago = datetime.now() - timedelta(days=366)
    unix_timestamp_one_year_ago = int(one_year_ago.timestamp())

    one_week_ago = datetime.now() - timedelta(days=7)
    unix_timestamp_one_week_ago = int(one_week_ago.timestamp())

    one_day_ago = datetime.now() - timedelta(hours=24)
    unix_timestamp_one_day_ago = int(one_day_ago.timestamp())

    # Providing data from inception for demo, need to restrict till a year
    # data = mdb.get("transactions", {"status": "confirmed", "updated_at": {'$exists': True, '$gt': unix_timestamp_one_year_ago}}, projection={"btc_amount": 1, "usd_amount": 1, "updated_at": 1, "status": 1})
    transactions = mdb.get("transactions", {"status": "confirmed", 'updated_at': {'$exists': True, "$type": 'int'}, 'usd_amount': {'$exists': 1}})
    accounts = mdb.get("users", {"account_type": {"$ne": "admin"}})

    per_day_transactions = list(filter(lambda _transaction: _transaction["updated_at"] > unix_timestamp_one_day_ago, transactions))
    per_week_transactions = list(filter(lambda _transaction: _transaction["updated_at"] > unix_timestamp_one_week_ago, transactions))

    data = {
        "transactions": {
            "day": sum(map(lambda _transaction: _transaction["usd_amount"], per_day_transactions)),
            "week": sum(map(lambda _transaction: _transaction["usd_amount"], per_week_transactions)),
            "year": sum(map(lambda _transaction: _transaction["usd_amount"], transactions)),
        },
        "fees": {
            "day": btcdc.convert(sum(map(lambda _transaction:  _transaction.get("transaction_fee", 0), per_day_transactions)), "btc")["_to"]["amount"],
            "week": btcdc.convert(sum(map(lambda _transaction:  _transaction.get("transaction_fee", 0), per_week_transactions)), "btc")["_to"]["amount"],
            "year": btcdc.convert(sum(map(lambda _transaction:  _transaction.get("transaction_fee", 0), transactions)), "btc")["_to"]["amount"],
        },
        "accounts": {
            "total": len(accounts),
            "active": len(list(filter(lambda _account: _account.get('active') == 1, accounts))),
            "inactive": len(accounts) - len(list(filter(lambda _account: _account.get('active') == 1, accounts))),
            "locked": 0
        }
    }

    return responsify(data)
from .handlers import create_blueprint
from .handlers.user import User
from src.utils import responsify
from src.utils.args_schema import token_args, auth_args, email_args, password_args, currency_args, admin_stats_args, set_user_balance_args, transactions_filter_args
from src.settings import mdb, btcdc, btc_node
from datetime import datetime, timedelta
from flask import request

bp, route = create_blueprint("admin", __name__, "/admin")

@route('/login', ["POST"], auth_args, _auth=None)
def admin_login(*args, **kwargs):
    account_type = kwargs.get("account_type")
    if (account_type and account_type != "admin"):
        return responsify({"error": "Invalid account_type"}, )
    return responsify(*User.login(account_type="admin", **kwargs))

@route('/stats', _identity=True, _args=currency_args)
def stats(_user, currency="usd"):

    if (_user.account_type != "admin"):
        return responsify({"error": "Unauthorized"}, 401)

    one_year_ago = datetime.now() - timedelta(days=366)
    unix_timestamp_one_year_ago = int(one_year_ago.timestamp())

    one_week_ago = datetime.now() - timedelta(days=7)
    unix_timestamp_one_week_ago = int(one_week_ago.timestamp())

    one_month_ago = datetime.now() - timedelta(days=30)
    unix_timestamp_one_month_ago = int(one_month_ago.timestamp())

    one_day_ago = datetime.now() - timedelta(hours=24)
    unix_timestamp_one_day_ago = int(one_day_ago.timestamp())

    admin_stats = mdb.get("admin_stats")
    if admin_stats:
        admin_stats = admin_stats[0]

        stats_currency = admin_stats.get("currency", "usd")

        admin_stats["transactions"] = dict(map(lambda y: [y[0], y[1]] if stats_currency == currency else [y[0], float(btcdc.convert(y[1], stats_currency)["_to"]["amount"])], filter(lambda x: x[1] != -1, admin_stats.get("transactions", {}).items())))
        admin_stats["fees"] = dict(map(lambda y: [y[0], y[1]] if stats_currency == currency else [y[0], float(btcdc.convert(y[1], stats_currency)["_to"]["amount"])], filter(lambda x: x[1] != -1, admin_stats.get("fees", {}).items())))
        admin_stats["accounts"] = dict(filter(lambda x: x[1] != -1, admin_stats.get("accounts", {}).items()))
        admin_stats["misc"] = dict(filter(lambda x: x[1] != -1, admin_stats.get("misc", {}).items()))
    else:
        admin_stats = {}

    transactions = mdb.get("transactions", {"status": "confirmed", "initiated_at": {'$exists': True, '$gt': unix_timestamp_one_year_ago}, 'usd_amount': {'$exists': 1}})
    accounts = mdb.get("users", {"account_type": {"$ne": "admin"}})

    per_day_transactions = list(filter(lambda _transaction: _transaction["initiated_at"] > unix_timestamp_one_day_ago, transactions))
    per_week_transactions = list(filter(lambda _transaction: _transaction["initiated_at"] > unix_timestamp_one_week_ago, transactions))
    per_month_transactions = list(filter(lambda _transaction: _transaction["initiated_at"] > unix_timestamp_one_month_ago, transactions))


    _transactions =  {
        "daily": sum(map(lambda _transaction: _transaction["usd_amount"], per_day_transactions)),
        "weekly": sum(map(lambda _transaction: _transaction["usd_amount"], per_week_transactions)),
        "monthly": sum(map(lambda _transaction: _transaction["usd_amount"], per_month_transactions)),
        "yearly": sum(map(lambda _transaction: _transaction["usd_amount"], transactions)),
    }

    _fees = {
        "daily": sum(map(lambda _transaction:  _transaction.get("transaction_fee", 0), per_day_transactions)),
        "weekly": sum(map(lambda _transaction:  _transaction.get("transaction_fee", 0), per_week_transactions)),
        "monthly": sum(map(lambda _transaction:  _transaction.get("transaction_fee", 0), per_month_transactions)),
        "yearly": sum(map(lambda _transaction:  _transaction.get("transaction_fee", 0), transactions)),

    }

    data = {
        "transactions": {**{k: v if currency == 'usd' else float(btcdc.convert(v, "usd")["_to"]["amount"]) for k, v in _transactions.items()}, **admin_stats.get("transactions", {})},
        "fees": {**{k: v if currency == 'btc' else float(btcdc.convert(v, "btc")["_to"]["amount"]) for k, v in _fees.items()}, **admin_stats.get("fees", {})},
        "accounts": {
            "total": len(accounts),
            "active": len(list(filter(lambda _account: _account.get('active') == 1, accounts))),
            "inactive": len(accounts) - len(list(filter(lambda _account: _account.get('active') == 1, accounts))),
            "locked": 0,
            "new": len(list(filter(lambda _account: _account.get('created_at') > unix_timestamp_one_day_ago, accounts))),
            **admin_stats.get("accounts", {})
        },
        **admin_stats.get("misc", {})
    }

    return responsify(data)


@route('/stats', ["PATCH"], _args=admin_stats_args, _identity=True)
def update_stats(_user, *args, **kwargs):

    if (_user.account_type != "admin"):
        return responsify({"error": "Unauthorized"}, 401)

    _id_query = {}
    admin_stats = mdb.get("admin_stats")
    if admin_stats:
        admin_stats = admin_stats[0]
        _id_query = { "_id": admin_stats["_id"]}
    else:
        admin_stats = {}

    admin_stats["transactions"] = { **admin_stats.get("transactions", {}), **kwargs.get("transactions", {})}
    admin_stats["fees"] = { **admin_stats.get("fees", {}), **kwargs.get("fees", {})}
    admin_stats["accounts"] = { **admin_stats.get("accounts", {}), **kwargs.get("accounts", {})}
    admin_stats["misc"] = { **admin_stats.get("misc", {}), **kwargs.get("misc", {})}
    admin_stats["currency"] = kwargs.get("currency", "usd")

    mdb.alter("admin_stats", _id_query, admin_stats, upsert=True)

    return responsify({"success": "Data updated successfully"})

@route('/btc-node-balance', _identity=True)
def node_balance(_user):

    if (_user.account_type != "admin"):
        return responsify({"error": "Unauthorized"}, 401)

    _balance = btc_node.get_balance()

    response = {
        "balance": _balance,
        "in_usd": float(btcdc.convert(_balance, "btc")["_to"]["amount"])
    }

    return responsify(response)


@route('/user-balances', _identity=True)
def list_user_balances(_user):

    if (_user.account_type != "admin"):
        return responsify({"error": "Unauthorized"}, 401)

    response = mdb.get("users", {"account_type": {"$ne": "admin"}, "balances": {"$exists": 1}}, {"_id": 0, "email": 1, "balances": 1, "account_type": 1})

    return responsify(response)


@route('/user-balance', ["PUT"], _args=set_user_balance_args, _identity=True)
def set_user_balance(_user, email, amount, currency="btc", force=None):

    if (_user.account_type != "admin"):
        return responsify({"error": "Unauthorized"}, 401)

    try:
        user = User.from_email(email)
    except Exception as e:
        print(e)
        return responsify({"error": "Invalid user email."}, 400)

    node_balance = btc_node.get_balance()

    if currency == "usd":
        node_balance = float(btcdc.convert(node_balance, "btc")["_to"]["amount"])

    if not force and amount > node_balance:
        return responsify({"error": "Insufficient balance."}, 400)

    user_balances = user.balances
    user_balances[currency] = amount

    user.push({"balances": user_balances})

    return responsify({"success": "User balance set succesfully"})


@route('/transactions', ["GET"], _args=transactions_filter_args, _identity=True)
def get_transactions(_user, *args, **kwargs):

    if (_user.account_type != "admin"):
        return responsify({"error": "Unauthorized"}, 401)

    year = kwargs.get("year")
    month = kwargs.get("month")

    if month and not year:
        return responsify({"error": "year is required with month"}, 400)

    query = {}
    if year or month:
        query = {
            'processed_at': {'$regex': f'^{year}-{month or "*"}-'}
        }

    records = mdb.get('manually_uploaded_transactions', query, {'_id': 0})

    total = {
        "total_records": len(records),
        "total_amount": sum(d.get("amount", 0) for d in records),
        "total_fee_collected": sum(d.get("fee_collected", 0) for d in records)
    }

    return responsify({"data": records,  **total})

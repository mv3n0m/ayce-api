from flask import request
from src.settings import btcdc
from src.utils import responsify
from .handlers import create_blueprint
from src.utils.args_schema import invoice_args
from src.utils.validations import validate_currency

bp, route = create_blueprint("misc", __name__)


@route("/currency-conversion", ["GET"], _auth=None)
def get_conversion_rate(*args, **kwargs):
    params = request.args
    keys = list(params.keys())

    if keys and any((k not in ["amount", "currency"] for k in keys)):
        return responsify({"error": 'Invalid query params. Allowed params: ["amount", "currency"]'}, 400)

    amount = params.get("amount")
    currency = params.get("currency")

    if amount and not currency:
        return responsify({"error": "'currency' is required for the provided 'amount'"}, 400)

    try:
        validate_currency(currency)
        amount = float(amount)
    except Exception as e:
        return responsify({"error": str(e)}, 400)

    # do apply a check for currency options
    return responsify(btcdc.convert(amount, currency), 200)
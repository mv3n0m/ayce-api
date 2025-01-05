from flask import request
from src.settings import mdb
from src.utils.args_schema import payment_information_args
from src.utils import responsify
from .handlers import create_blueprint

bp, route = create_blueprint("settings", __name__, "/settings")


## Make these global values, settings values embedded in JWT itself for further cases
# in order to decrease db calls
@route("/payment-information", ["POST", "GET"], payment_information_args)
def set_payment_information(merchant_id, *args, **kwargs):

    if request.method == "GET":
        return mdb.get_by__id("users", merchant_id, {"_id": 0, "split_settlement": 1, "native_currency": 1, "auto_conversion": 1})

    native_currency = kwargs.get("native_currency", "usd").lower()
    split_settlement = kwargs.get("split_settlement", 0)

    kwargs.update({
        "native_currency": native_currency,
        "split_settlement": split_settlement
    })

    mdb.alter("users", {"_id": merchant_id}, kwargs)

    return responsify({"success": "Payment information updated successfully."})
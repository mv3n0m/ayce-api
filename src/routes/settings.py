from flask import request
from src.settings import mdb
from src.utils.args_schema import payment_information_args
from src.utils import create_blueprint, responsify, check_jwt_tokens


bp, use_kwargs = create_blueprint("settings", __name__, "/settings")


@bp.route("/payment-information", methods=["POST", "GET"])
@use_kwargs(payment_information_args)
def set_payment_information(*args, **kwargs):
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    if request.method == "GET":
        return mdb.get("merchants", mdb_query, {"_id": 0, "split_settlement": 1, "native_currency": 1, "auto_conversion": 1})[0]

    native_currency = kwargs.get("native_currency", "usd").lower()
    split_settlement = kwargs.get("split_settlement", 0)

    kwargs.update({
        "native_currency": native_currency,
        "split_settlement": split_settlement
    })

    mdb.alter("merchants", mdb_query, kwargs)

    return responsify({"success": "Payment information updated successfully."})
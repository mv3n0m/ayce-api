import random
import logging
import requests
from uuid import uuid4
from flask import request
from src.settings import mdb, tknz, btcdc, rst, mailer
from src.utils import responsify
from src.utils.args_schema import token_args, otp_args, auth_args, email_args, password_args, user_info_args, invoice_args
from .handlers import create_blueprint
from .handlers.user import User


bp, route = create_blueprint("account", __name__, "/account")


@route("/scheduled-transfers", ["POST", "GET"], _identity=True)
def scheduled_transfers(merchant):
	if request.method == "GET":
		return responsify(merchant.schedules)

	request_json = request.json

	if not all((i in ["usd", "btc", "btc_address"] for i in request_json.keys())):
		return responsify({"error": "Invalid keys in json body."}, 400)

	# instead of false get the value from inside the record and ultimately a false if nothing (like ternary)
	btc = request_json.get("btc", False)
	usd = request_json.get("usd", False)
	btc_address = request_json.get("btc_address")

	if not isinstance(btc, (str, bool)):
		return responsify({"error": "Value for btc can be either a boolean or a string."}, 400)

	if not isinstance(usd, (str, bool)):
		return responsify({"error": "Value for usd can be either a boolean or a string."}, 400)

	options = ["daily", "weekly"]
	if isinstance(btc, str) and btc not in options:
		return responsify({"error": f"Available options for btc -> {options}"}, 400)

	if isinstance(usd, str) and usd not in options:
		return responsify({"error": f"Available options for usd -> {options}"}, 400)

	if btc and not btc_address:
		return responsify({"error": "btc_address is required for a scheduled btc transfer"}, 400)

	otp = str(random.randrange(100000, 1000000))
	# replace with UUID
	token = str(merchant._id)

	try:
		data = {
			"mail_type": "scheduled transfers",
			"name": merchant.username or "User",
			"email": merchant.email,
			"payload": {
				"otp": otp,
				"company_name": "{Mechant's company name}",
				"contact_information": "{Merchant's company information}",
				# "creation_date": str(datetime.fromtimestamp(invoice.get("created_at"))).split(" ")[0]
			}
		}
		mailer.send(data)
	except Exception as e:
		print(e)
		return responsify({"error": "Failed to send scheduled transfer updated confirmation email."}, 500)

	rst._set(token, otp)
	mdb.alter("users", {"_id": token}, {"schedules": {"status": "pending", **request_json}})

	return responsify({"success": "OTP sent to user's email.", "token": token}, 200)


@route("/scheduled-transfers/otp-confirm", ["POST", "GET"], { **token_args(), **otp_args}, _identity=True)
def scheduled_transfers_confirm(merchant, token, otp):
	_status = rst._get(token)
	if _status.get("error"):
		return responsify({"error": "Unable to confirm OTP."}, 400)

	status = _status.get("status")
	if not status or status == 'None':
		return responsify({"error": "Unable to confirm OTP."}, 400)

	if otp != status:
		return responsify("Invalid OTP.", 401)

	rst._del(token)

	mdb.alter("users", {"_id", merchant._id}, {"schedules.status": "confirmed"})
	print("completed")

	return responsify({"success": "Scheduled transfers states updated."}, 200)


@route("/get-transactions")
def get_transactions(merchant_id):
    _query = {
      "$or": [
        {"merchant_id": merchant_id},
        {"recipient_id": merchant_id}
      ],
      "status": {"$ne": "expired"}
    }

    # give transactions in descending order of date initiated
    response = mdb.get("transactions", _query, {"_id": 0, "on_hold": 0})

    for r in response:
      if r.get("recipient_id") == merchant_id:
        r["type"] = "receive"

    return responsify({"transactions": response}, 200)


@route("/get-balances", _identity=True)
def get_balances(merchant):
    balances = merchant.balances or {"usd": 0, "btc": 0}
    usd, btc = balances["usd"], balances["btc"]

    balances["usd"] = {
        "amount": f"{round(usd, 4)}",
        "in_btc": btcdc.convert(usd, "usd")["_to"]["amount"]
    }

    balances["btc"] = {
        "amount": f"{round(btc, 8):.8f}",
        "in_usd": btcdc.convert(btc, "btc")["_to"]["amount"]
    }

    return responsify(balances, 200)


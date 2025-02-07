import random
import logging
import requests
from uuid import uuid4
from flask import request
from src.settings import mdb, tknz, btcdc, rst, mailer
from src.utils import responsify
from src.utils.args_schema import token_args, otp_args, auth_args, email_args, password_args, user_info_args, invoice_args, scheduled_transfer_args
from .handlers import create_blueprint
from .handlers.user import User


bp, route = create_blueprint("account", __name__, "/account")


@route("/scheduled-transfers", ["GET"], _identity=True)
def get_scheduled_transfers(merchant):
	return responsify(merchant.schedules["active"])


@route("/scheduled-transfers", ["POST"], scheduled_transfer_args, _identity=True)
def post_scheduled_transfers(merchant, btc=None, usd=None, btc_address=None, *args, **kwargs):

	if not (btc or usd):
		return responsify({"error": "Either btc or usd value required."}, 400)
	
	if btc and usd:
		return responsify({"error": "Either btc or usd value accepted in single request."}, 400)

	if btc and not btc_address:
		return responsify({"error": "btc_address is required for a scheduled btc transfer"}, 400)

	otp = str(random.randrange(100000, 1000000))
	token = str(uuid4())

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
		return responsify({"error": "Failed to send scheduled transfer update confirmation email."}, 500)

	rst._set(token, otp)

	_key = "usd" if usd else "btc"
	merchant_schedules = merchant.schedules or {}
	pending_merchant_schedules = merchant_schedules.get("pending", {})
	pending_merchant_schedules[_key] = {
		"period": usd or btc,
		"recipient": btc_address,
		"token": token
	}

	merchant_schedules["pending"] = pending_merchant_schedules

	mdb.alter("users", {"_id": merchant._id}, {"schedules": merchant_schedules})

	return responsify({"success": "OTP sent to merchant's email.", "token": token, "totp": otp}, 200)


@route("/scheduled-transfers/resend-otp", ["POST"], token_args(), _identity=True)
def scheduled_transfers_resend(merchant, token):
	otp = str(random.randrange(100000, 1000000))

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
		return responsify({"error": "Failed to resend scheduled transfer update confirmation email."}, 500)

	rst._set(token, otp)

	return responsify({"success": "OTP resent to merchant's email.", "totp": otp}, 200)


@route("/scheduled-transfers/confirm", ["POST"], { **token_args(), **otp_args}, _identity=True)
def scheduled_transfers_confirm(merchant, token, otp):
	
	merchant_schedules = merchant.schedules or {}
	pending_merchant_schedules = merchant_schedules.get("pending", {})

	_schedule_item = next(filter(lambda x: x[1]["token"] == token, pending_merchant_schedules.items()), None)
	if not _schedule_item:
		return responsify({"error": "Invalid token"}, 400)
	_key, _schedule = _schedule_item
	
	status = rst._get(token)

	if not status or status == 'None':
		return responsify({"error": "Unable to confirm OTP."}, 400)

	if otp != status:
		return responsify({"error": "Invalid OTP."}, 401)

	rst._del(token)

	del _schedule["token"]
	active_merchant_schedules = merchant_schedules.get("active", {})
	active_merchant_schedules[_key] = _schedule
	merchant_schedules["active"] = active_merchant_schedules
	del merchant_schedules["pending"][_key]

	mdb.alter("users", {"_id": merchant._id}, {"schedules": merchant_schedules})

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
		r["mechant_id"] = str(r.get("merchant_id", ""))
		r["recipient_id"] = str(r.get("recipient_id", ""))

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


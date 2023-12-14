import random
import requests
from .handlers import create_blueprint
from src.settings import mdb, rst, mailer
from src.utils import responsify, get_token_otp_pair, get_token
from src.utils.args_schema import developer_key_args, token_otp_args, token_args, simulator_args


bp, route = create_blueprint("developers", __name__, "/developers")

@route("/list-api-keys")
def list_keys(user_id, *args, **kwargs):
	data = mdb.get("developer_keys", {"user_id": user_id, "active": 1,  "api-key": {"$exists": 1}}, {"_id": 0, "user_id": 0})

	return responsify(data, 200)


@route("/add-api-key", ["POST"], developer_key_args, _auth="_jwt")
def add_key(user, *args, **kwargs):
	if mdb.get("developer_keys", {"user_id": user._pk, "active": 1, "label": kwargs["label"]}):
		return responsify({"error": "Developer API key label already exists."}, 400)

	token, otp = get_token_otp_pair()

	try:
		data = {
			"mail_type": "developer key addition",
			"name": user.username or "User",
			"email": user.email,
			"payload": {
				"otp": otp,
				"company_name": "Ayce Express",
				"contact_information": "",
			}
		}
		mailer.send(data)
	except Exception as e:
		print(e)
		return {"error": "Failed to send verification email."}, 500

	rst._set(token, otp)
	mdb.add("developer_keys", { "user_id": user._pk, "active": 0, "token": token, **kwargs })

	return responsify({"success": "OTP sent to user's email.", "token": token}, 201)


@route("/add-api-key/otp-confirm", ["POST"], token_otp_args)
def confirm_key_addition(*args, **kwargs):

	token = kwargs["token"]
	otp = kwargs["otp"]

	try:
		value = rst._get(token)
	except Exception as e:
		return responsify({"error": e.__str__()}, 400)

	if not value or value == 'None':
		return responsify({"error": "Unable to confirm OTP."}, 400)

	if otp != value:
		return responsify("Invalid OTP.", 401)

	rst._del(token)
	mdb.alter("developer_keys", {"token": token}, {"active": 1, "api-key": get_token()}, {"token": 1})

	return responsify({"success": "Developer API key confirmed successfully."}, 200)


@route("/revoke-api-key", ["POST"], token_args("api-key"))
def revoke_key(user_id, *args, **kwargs):
	api_key = kwargs["api-key"]
	record = mdb.get("developer_keys", {"user_id": user_id, "api-key": kwargs["api-key"]})

	if not record:
		return responsify({"error": "Invalid API key."}, 400)
	record = record[0]

	mdb.alter("developer_keys", {"_id": record["_id"]}, {"active": 0})

	return responsify({"success": "Developer API key revoked successfully."}, 200)


@route("/generate-ecommerce-key")
def generate_ecommerce_key(user_id, *args, **kwargs):
	token = get_token()
	mdb.add("developer_keys", {"user_id": user_id, "active": 0, "ecommerce-key": token})

	return responsify({"ecommerce-key": token}, 201)


@route("/webhook-simulator", ["POST"], simulator_args)
def webhook_simulator(*args, **kwargs):

	url = kwargs["callback_url"]
	response = requests.get(url, params={"status": kwargs["status"], "transaction_id": get_token()})
	if response.status_code != 200:
		print(response.content)
		return responsify({"error": "Invalid callback url. OR, Failed to make request."}, 500)

	return responsify({"success": "The callback url has been hit with the required params."}, 200)

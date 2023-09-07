import time
import random
import logging
import requests
from uuid import uuid4
from bson import ObjectId
from flask import request, Response
from datetime import datetime, timedelta
from src.services.aws import enqueue_transaction
from src.settings import btc_node, mdb, rst, tknz, mailer, btcdc
from src.utils import create_blueprint, responsify, check_jwt_tokens
from src.utils.args_schema import wallet_name_args, token_args, transaction_args, exchange_args, transfer_args, otp_args, invoice_args, payouts_args, payment_buttons_args


bp, use_kwargs = create_blueprint("transactions1", __name__, "/transactions1")

@bp.route("/collect-payment-details", methods=["POST"])
@use_kwargs(payment_buttons_args)
def record_payments(*args, **kwargs):
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    merchant_id = mdb_query.get('merchant_id')

    token = "pay" + str(uuid4())
    image = kwargs.pop("image", None)
    if image:
        pass

    now = int(datetime.now().timestamp())
    kwargs.update({
        "payment_token": token,
        "merchant_id": merchant_id,
        "initiated_at": now,
        "status": "pending"
    })

    mdb.add("payments", kwargs)

    return responsify({"payment_token": token, "success": "Payment record created."}, 201)


@bp.route("/get-payment-details/<payment_token>", methods=["GET"])
def fetch_collectibles(payment_token):
    response = mdb.get("payments", {"payment_token": payment_token}, {"_id": 0, "merchant_id": 0})
    if not response:
        return responsify({"error": "Invalid payment token"}, 400)
    response = response[0]

    return responsify(response, 200)


@bp.route("/list-payments", methods=["GET"])
def list_payments():
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    merchant_id = mdb_query.get('merchant_id')

    response = mdb.get("payments", {"merchant_id": merchant_id}, {"_id": 0, "merchant_id": 0, "payer_details.updated_at": 0})

    return responsify(response, 200)


@bp.route("/update-payment-collectibles/<payment_token>", methods=["POST"])
def update_payment_collectibles(payment_token):
    response = mdb.get("payments", {"payment_token": payment_token}, {"_id": 0, "merchant_id": 0})
    if not response:
        return responsify({"error": "Invalid payment token"}, 400)
    response = response[0]

    payer_details = {"updated_at": int(datetime.now().timestamp())}
    request_json = request.json
    collectibles = response.get("collectibles", [])
    collectibles += response.get("additional", [])

    for k, v in request_json.items():
        if k in collectibles:
            payer_details [k] = v
        else:
            return responsify({"error": f"Invalid collectible: {k}"}, 400)

    remaining = set(collectibles).difference(set(payer_details))
    if remaining:
        return responsify({"error": f"Missing required item/s: {list(remaining)}"}, 400)

    mdb.alter("payments", {"payment_token": payment_token}, {"payer_details": payer_details})

    return responsify({"success": "Payment collectibles updated."}, 200)


@bp.route("/payouts", methods=["POST"])
@use_kwargs(payouts_args)
def record_payouts(records, notes=""):
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    merchant_id = mdb_query.get('merchant_id')

    deductions = {"usd": 0, "btc": 0}

    all_addresses = [user.get("email") for user in mdb.get("merchants", {}, {"email": 1})]

    for record in records:
        address_type = record.get("address_type", "email").lower()
        address = record.get("address").lower()
        source_wallet = record.get("source_wallet").lower()
        currency = record.get("currency").lower()
        amount = record.get("amount")

        if address_type == "email" and address not in all_addresses:
            return responsify({"error": f"No user found with email: {address}"})

        if currency != source_wallet:
            amount = float(btcdc.convert(amount, currency)["_to"]["amount"])

        if source_wallet == "usd":
            amount = tknz.get_exchange_values(amount, "usd", "btc")["required_amount"]

        deductions[source_wallet] += amount

    merchant = mdb.get("merchants", mdb_query)[0]
    balances = merchant.get("balances")

    for k, v in deductions.items():
        if balances[k] < v:
            return responsify({"error": f"Insufficient balance in {k.upper()} wallet."}, 400)

    otp = str(random.randrange(100000, 1000000))
    inserted_id = mdb.add("payouts", {"status": "pending", "records": records, "merchant_id": merchant_id, "merchant_deductions": deductions, "notes": notes})
    token = str(inserted_id)

    try:
        data = {
            "mail_type": "payouts",
            "name": merchant.get("username", "User"),
            "email": merchant.get("email"),
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
        return responsify({"error": "Failed to send payouts confirmation email."}, 500)

    rst._set(token, otp)
    response = {"token": token, "success": "OTP sent to mechant's email."}

    return responsify(response, 201)


@bp.route("/payouts/otp-confirm", methods=["POST"])
@use_kwargs({ **token_args, **otp_args})
def confirm_payouts(token, otp):
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    merchant_id = mdb_query.get('merchant_id')

    merchant = mdb.get("merchants", mdb_query)[0]
    merchant_email = merchant.get("email")

    payouts = mdb.get("payouts", { "_id": ObjectId(token) })
    if not payouts:
        return responsify({"error": "Invalid payouts token."}, 400)

    payouts = payouts[0]
    if payouts.get("merchant_id") != merchant_id:
        return responsify({"error": "Unauthorized"}, 401)

    _status = rst._get(token)
    if _status.get("error"):
        return responsify({"error": "Unable to confirm OTP."}, 400)

    status = _status.get("status")
    if not status or status == 'None':
        return responsify({"error": "Unable to confirm OTP."}, 400)

    if otp != status:
        return responsify("Invalid OTP.", 401)

    rst._del(token)

    for record in payouts['records']:
        address_type = record.get("address_type", "email").lower()
        address = record.get("address").lower()
        source_wallet = record.get("source_wallet").lower()
        currency = record.get("currency").lower()
        amount = record.get("amount")

        if currency == "usd":
            if source_wallet == "usd":
                btc_amount = tknz.get_exchange_values(amount, "usd", "btc")["_to"]["amount"]
            else:
                btc_amount = float(btcdc.convert(amount, currency)["_to"]["amount"])
        else:
            btc_amount = amount
            amount = float(btcdc.convert(amount, "btc")["_to"]["amount"])

        now = int(datetime.now().timestamp())
        transaction = {
            "type": "transfer",
            "receiver": address,
            "description": f"Payout {merchant_email} -> {record['address']}",
            "btc_amount": btc_amount,
            "usd_amount": amount,
            "initiated_at": now,
            "merchant_id": merchant_id,
            "status": "confirmed",
        }

        if address_type in ["ayce_id", "email"]:
            rmdb_query = {record["address_type"]: record["address"]}
            inc_query = {f"balances.btc": btc_amount}

            mdb.alter("merchants", rmdb_query, inc=inc_query)

            _id = record["address"]
            if address_type == "email":
                _id = mdb.get("merchants", rmdb_query)[0]["merchant_id"]

            transaction.update({
                "recipient_id": _id
            })
        else:
            status_code, content = btc_node.transfer(btc_amount, address)
            if status_code != 200:
                print(content)
                return responsify({"error": "Failed to transfer BTC"}, 500)

            transaction_id = content.get("result")
            blockExplorer = f"https://blockstream.info/testnet/tx/{transaction_id}"

            transaction.update({
                "updated_at": int(datetime.now().timestamp()),
                "transaction_id": transaction_id,
                "blockExplorer": blockExplorer,
                "transaction_label": f"{now}m{merchant_id}"
            })

        mdb.add("transactions", transaction)

    merchant_deductions = {f"balances.{k}": -v for k, v in payouts["merchant_deductions"].items()}
    mdb.alter("merchants", mdb_query, inc=merchant_deductions)

    return responsify({"success": "Payouts successfully queued."}, 200)


@bp.route("/create-invoice", methods=["POST"])
@use_kwargs(invoice_args)
def create_invoice(*args, **kwargs):
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    merchant_id = mdb_query.get('merchant_id')

    invoice_number = kwargs.get("invoice_number")

    invoice_existence = mdb.get("invoices", {"merchant_id": merchant_id, "invoice_number": invoice_number})
    if invoice_existence:
        return responsify({"error": f"Invoice number: {invoice_number} already exists."}, 400)

    invoice_token = str(uuid4())

    misc = {
        "invoice_token": invoice_token,
        "status": "unpaid",
        "merchant_id": merchant_id,
        "created_at": int(datetime.utcnow().timestamp()),
        "due_date": str(kwargs.get("due_date")).split("T")[0]
    }
    kwargs.update(misc)

    mdb.add("invoices", kwargs)

    return responsify({"success": "Invoice created successfully.", "invoice-token": invoice_token}, 201)


@bp.route("/get-invoice/<invoice_token>", methods=["GET"])
def get_invoice(invoice_token):
    invoice = mdb.get("invoices", { "invoice_token": invoice_token }, {"_id": 0 })
    if not invoice:
        return responsify({"error": "Invalid invoice token."}, 400)

    invoice = invoice[0]
    if invoice.get("status") in ["cancelled"]:
        return responsify({"error": f"Invoice already { invoice['status'] }."}, 400)

    merchant_id = invoice.pop("merchant_id")
    merchant = mdb.get("merchants", { "merchant_id": merchant_id })[0]

    invoice["merchant_name"] = merchant.get("username", "")
    invoice["merchant_email"] = merchant.get("email")

    return responsify(invoice, 200)


@bp.route("/list-invoices", methods=["GET"])
def list_invoices():
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    merchant_id = mdb_query.get('merchant_id')
    invoices = mdb.get("invoices", {"merchant_id": merchant_id}, {"_id": 0, "invoice_number": 1, "recipient_name": 1, "due_date": 1, "total_due": 1, "status": 1})

    return responsify(invoices, 200)


@bp.route("/send-invoice/<invoice_token>", methods=["GET"])
def send_invoice(invoice_token):
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    merchant_id = mdb_query.get('merchant_id')

    args = request.args
    if "invoice_link" not in args:
        return responsify({"error": "invoice_link not provided as query params"}, 400)

    invoice_link = args.get("invoice_link")

    invoice = mdb.get("invoices", { "invoice_token": invoice_token })
    if not invoice:
        return responsify({"error": "Invalid invoice token."}, 400)

    invoice = invoice[0]
    if invoice.get("merchant_id") != merchant_id:
        return responsify({"error": "Unauthorized"}, 401)

    if invoice.get("status") in ["paid", "cancelled"]:
        return responsify({"error": f"Invoice already { invoice['status'] }."}, 400)

    try:
        data = {
            "mail_type": "invoice",
            "name": invoice.get("recipient_name"),
            "email": invoice.get("recipient_email"),
            "payload": {
                "invoice_link": invoice_link,
                "invoice_number": invoice.get("invoice_number"),
                "company_name": "{Mechant's company name}",
                "contact_information": "{Merchant's company information}",
                "creation_date": str(datetime.fromtimestamp(invoice.get("created_at"))).split(" ")[0]
            }
        }
        mailer.send(data)
    except Exception as e:
        print(e)
        return responsify({"error": "Failed to send invoice email."}, 500)

    return responsify({"success": "Invoice sent successfully.", "invoice-token": invoice_token}, 200)


@bp.route("/cancel-invoice/<invoice_token>", methods=["GET"])
def cancel_invoice(invoice_token):
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    merchant_id = mdb_query.get('merchant_id')

    invoice = mdb.get("invoices", { "invoice_token": invoice_token })
    if not invoice:
        return responsify({"error": "Invalid invoice token."}, 400)

    invoice = invoice[0]
    if invoice.get("merchant_id") != merchant_id:
        return responsify({"error": "Unauthorized"}, 401)

    if invoice.get("status") == "cancelled":
         return responsify({"error": "Invoice cancelled already."}, 400)

    mdb.alter("invoices", { "invoice_token": invoice_token }, {"status": "cancelled", "updated_at": int(datetime.utcnow().timestamp())})

    return responsify({"success": "Invoice cancelled successfully.", "invoice-token": invoice_token}, 200)


@bp.route("/create-wallet", methods=["POST"])
@use_kwargs(wallet_name_args)
def create_wallet(wallet_name):
    status_code, content = btc_node.get_node("on-chain").create_wallet(wallet_name)

    if status_code != 200:
        return responsify({"error": "Wallet creation failed"}, 400)

    return responsify({"success": f"{wallet_name} wallet created successfully."}, 201)


@bp.route("/get-new-address", methods=["POST"])
@use_kwargs(wallet_name_args)
def get_new_address(wallet_name):
    status_code, content = btc_node.get_node("on-chain").create_new_address(wallet_name)

    if status_code != 200:
        return responsify({"error": "Address creation failed"}, 400)

    return responsify({"wallet_name": wallet_name, "address": content.get("result")}, 201)


@bp.route("/pos/create-transaction", methods=["POST"])
@use_kwargs(transaction_args)
def create_transaction(amount, description="Ayce POS transaction"):

    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    merchant = mdb.get("merchants", mdb_query, {"_id": 0})
    merchant_id = mdb_query.get('merchant_id')

    merchant = merchant[0]
    balances = merchant.get("balances", {"usd": 0, "btc": 0})
    usd, btc = balances["usd"], balances["btc"]

    response = tknz.get_price()
    if response.get("error"):
        return responsify({"Unable to fetch conversion rate"}, 500)

    price = float(response.get("price"))


    btc_value = amount / price

    now = int(datetime.utcnow().timestamp())
    label = f"{now}m{merchant_id}"

    addresses = btc_node.get_payment_addresses({"amount": btc_value, "label": label, "description": description})

    if addresses.get("error"):
        return responsify({"error": "Failed to create payment address"}, 400)

    transaction = {
        "btc_amount": btc_value,
        "usd_amount": amount,
        "transaction_label": label,
        "merchant_id": merchant_id,
        "description": description,
        "type": "receive",
        "status": "pending",
        "initiated_at": now,
        **addresses
    }

    inserted_id = mdb.add("transactions", transaction)
    response = {"token": str(inserted_id), "conversion_rate": f"${price} BTC/USD"}

    return responsify(response, 201)


@bp.route("/pos/get-payment-addresses", methods=["POST"])
@use_kwargs(token_args)
def get_payment_addresses(token):

    transaction = mdb.get("transactions", {"_id": ObjectId(token)}, {"_id": 0, "type": 0, "merchant_id": 0, "status": 0})
    if not transaction:
        return responsify({"error": "Incorrect token."}, 400)

    transaction = transaction[0]
    label = transaction.get("transaction_label")

    enqueue_transaction({
        "transaction_label": label,
        "callback_urls": [
            (request.host_url.split("://")[1].strip("/"), "/transactions/pos/settle-invoice")
        ]
    })

    rst._set(label)

    return responsify(transaction, 200)


@bp.route("/pos/settle-invoice")
def settle_invoice():

    params = request.args
    transaction_label = params.get("transaction_label")
    status = params.get("status", "expired")

    transaction = mdb.get("transactions", {"transaction_label": transaction_label})
    if not transaction:
        return responsify({}, 400)
    transaction = transaction[0]

    if not transaction.get("status") == "pending":
        return responsify({}, 400)

    tid, mid = transaction_label.split("m")

    mdb_query = {"merchant_id": mid}
    merchant = mdb.get("merchants", mdb_query)[0]

    balances = merchant.get("balances", {"usd": 0, "btc": 0})
    btc_amount = transaction.get("btc_amount", 0)
    transaction_fee = btc_amount * 0.01

    if status == "confirmed":
        if not balances.get("btc"):
            balances["btc"] = 0
        if not balances.get("usd"):
            balances["usd"] = 0

        btc_to_be_settled = btc_amount - transaction_fee
        if merchant.get("auto_conversion"):
            split_settlement = merchant.get("split_settlement", 0)
            btc_calculated = btc_to_be_settled * (split_settlement / 100)
            usd_to_be_settled = tknz.get_exchange_values(btc_to_be_settled - btc_calculated, "btc", "usd")
            tknz.exchange(usd_to_be_settled["btc_amount"], "btc", "usd")
            balances["usd"] += usd_to_be_settled["usd_amount"]
            print(usd_to_be_settled["usd_amount"])
            btc_to_be_settled = btc_calculated

        balances["btc"] += btc_to_be_settled
        print(balances)

    mdb.alter("transactions", {"transaction_label": transaction_label}, {"status": status, "updated_at": int(datetime.now().timestamp()), "payment_mode": "lightning", "transaction_fee": transaction_fee})
    mdb.alter("merchants", mdb_query, {"balances": balances})
    rst._set(transaction_label, status)

    return responsify({}, 200)


@bp.route("/pos/payment-status/<transaction_label>")
def invoice_status(transaction_label):
    initial_datetime = datetime.now()
    expected_datetime = initial_datetime + timedelta(minutes=11)

    def eventStream():
        while True:
            if datetime.now() >= expected_datetime:
                transaction = mdb.get("transactions", {"transaction_label": transaction_label})
                if transaction and transaction[0].get("status") != "pending":
                    return responsify({"data": transaction[0]["status"]}, 200)
                return responsify({"error": "Timed out."}, 400)

            _status = rst._get(transaction_label)
            if _status.get("error"):
                return responsify(_status, 400)

            status = _status.get("status")
            if status and status != 'None':
                rst._del(transaction_label)
                return f"data: {status}\n\n"

            time.sleep(0.5)

    response = eventStream()
    if isinstance(response, Response):
        return response

    return Response(response, mimetype="text/event-stream")


@bp.route("/pos/settle-transaction", methods=["POST"])
def pos_settle_transaction():
    payload = request.json
    address = payload.pop("address", "na")
    amount = payload.pop("amount", 0)

    transaction_id = payload.get("transaction_id")
    if not transaction_id:
        return responsify({}, 200)
    logging.info(f"settle-transaction route hit for transaction: { transaction_id }")

    transaction = mdb.get("transactions", {"on-chain": address})
    if not transaction:
        return responsify({}, 400)
    transaction = transaction[0]
    label = transaction.get("transaction_label")

    _status = rst._get(label)
    if "error" in _status.keys():
        return responsify(_status, 400)

    status = _status.get("status")
    if status and status != 'None':
        return responsify({}, 200)

    merchant_id = transaction.get("merchant_id")
    merchant = mdb.get("merchants", {"merchant_id": merchant_id})[0]

    balances = merchant.get("balances", {"usd": 0, "btc": 0})
    if not balances.get("btc"):
        balances["btc"] = 0

    btc_amount = transaction.get("btc_amount", 0)
    transaction_fee = btc_amount * 0.01

    if not balances.get("btc"):
        balances["btc"] = 0
    if not balances.get("usd"):
        balances["usd"] = 0

    btc_to_be_settled = btc_amount - transaction_fee
    if merchant.get("auto_conversion"):
        split_settlement = merchant.get("split_settlement", 0)
        btc_calculated = btc_to_be_settled * (split_settlement / 100)

        usd_to_be_settled = tknz.get_exchange_values(btc_to_be_settled - btc_calculated, "btc", "usd")
        tknz.exchange(usd_to_be_settled["btc_amount"], "btc", "usd")
        balances["usd"] += usd_to_be_settled["usd_amount"]
        print(usd_to_be_settled["usd_amount"])
        btc_to_be_settled = btc_calculated

    balances["btc"] += btc_to_be_settled
    print(balances)

    status = "confirmed"

    payload.update({"status": status, "updated_at": int(datetime.now().timestamp()), "payment_mode": "on-chain", "transaction_fee": f"{transaction_fee:.8f} BTC"})
    rst._set(label, status)

    mdb.alter("transactions", {"on-chain": address}, payload)
    mdb.alter("merchants", {"merchant_id": merchant_id}, {"balances": balances})

    return responsify({}, 200)


@bp.route("/exchange/get-conversion-rate", methods=["POST"])
@use_kwargs(exchange_args)
def get_exchange_conversion_rate(amount, _from, _to, description="In-wallet conversion"):
    mdb_query = {"merchant_id": '12'}
    db_response = mdb.get("merchants", mdb_query, {"_id": 0})
    merchant_id = mdb_query.get('merchant_id')

    db_response = db_response[0]
    balances = db_response.get("balances", {"usd": 0, "btc": 0})

    response = tknz.get_exchange_values(amount, _from, _to)
    if response.get("error"):
        return responsify({"error": "Unable to fetch conversion rate"}, 500)

    _from = _from.lower()
    required_amount = response.pop("required_amount", 0)

    if balances.get(_from, 0) < required_amount:
        return responsify({"error": f"Insufficient {_from} balance"}, 400)

    balances[_from] -= required_amount

    now = int(datetime.utcnow().timestamp())
    label = f"{now}m{merchant_id}"

    transaction = {
        "transaction_label": label,
        "merchant_id": merchant_id,
        "description": description,
        "type": "conversion",
        "status": "pending",
        "initiated_at": now,
        "expiry": int((datetime.now() + timedelta(minutes=3)).timestamp()),
        "on_hold": {
            "currency": _from,
            "amount": required_amount
        },
        **response
    }

    inserted_id = mdb.add("transactions", transaction)
    response = {"token": str(inserted_id), **response}
    mdb.alter("merchants", mdb_query, {"balances": balances})

    return responsify(response, 201)


@bp.route("/exchange/refresh-conversion-rate", methods=["POST"])
@use_kwargs(token_args)
def refresh_exchange_rate(token):
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    merchant_id = mdb_query.get('merchant_id')

    transaction = mdb.get("transactions", {"_id": ObjectId(token)})
    if not transaction:
        return responsify({"error": "Invalid token."}, 400)
    transaction = transaction[0]

    if transaction.get("merchant_id") != merchant_id:
        return responsify({"error": "Incorrect token."}, 400)

    db_response = mdb.get("merchants", mdb_query, {"_id": 0})
    db_response = db_response[0]
    balances = db_response.get("balances", {"usd": 0, "btc": 0})

    on_hold = transaction.get("on_hold")
    if on_hold:
        balances[on_hold["currency"]] += balances[on_hold["amount"]]

    response = tknz.get_exchange_values(amount, _from, _to)
    if response.get("error"):
        return responsify({"error": "Unable to fetch conversion rate"}, 500)

    _from = _from.lower()
    required_amount = response.pop("required_amount", 0)

    if balances.get(_from, 0) < required_amount:
        return responsify({"error": f"Insufficient {_from} balance"}, 400)

    balances[_from] -= required_amount
    now = int(datetime.utcnow().timestamp())

    transaction = {
        "updated_at": now,
        "expiry": int((datetime.now() + timedelta(minutes=3)).timestamp()),
        "on_hold": {
            "currency": _from,
            "amount": required_amount
        },
        **response
    }

    mdb.alter("transactions", {"_id": ObjectId(token)}, transaction)
    response = {"token": token, **response}
    mdb.alter("merchants", mdb_query, {"balances": balances})

    return responsify(transaction, 201)


@bp.route("/exchange/confirm", methods=["POST"])
@use_kwargs(token_args)
def exchange_currencies(token):
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    merchant_id = mdb_query.get('merchant_id')

    transaction = mdb.get("transactions", {"_id": ObjectId(token)})
    if not transaction:
        return responsify({"error": "Invalid token."}, 400)
    transaction = transaction[0]

    if transaction.get("merchant_id") != merchant_id:
        return responsify({"error": "Incorrect token."}, 400)

    db_response = mdb.get("merchants", mdb_query, {"_id": 0})
    db_response = db_response[0]
    balances = db_response.get("balances", {"usd": 0, "btc": 0})

    on_hold = transaction.get("on_hold")
    if not on_hold:
        return responsify({"error": "Incorrect transaction."}, 400)

    if transaction.get("expiry") < datetime.now().timestamp():
        balances[on_hold["currency"]] += balances[on_hold["amount"]]
        mdb.alter("merchants", mdb_query, {"balances": balances})

        return responsify({"error": "Expired transaction"}, 400)

    _to = transaction["_to"]
    _from = transaction["_from"]
    if on_hold["currency"] == "btc":
        amount = on_hold["amount"]
    else:
        amount = _to["amount"]

    response = tknz.exchange(amount, _from["currency"], _to["currency"])
    order_id = response.get("order_id")

    balances[_to["currency"]] += _to["amount"]

    mdb.alter("transactions", {"_id": ObjectId(token)}, {"status": "confirmed", "updated_at": int(datetime.now().timestamp())}, {"on_hold": 0})
    mdb.alter("merchants", mdb_query, {"balances": balances})

    return responsify({"success": f"Exchanged { _from['amount'] } { _from['currency'].upper() } to { _to['amount'] } { _to['currency'].upper() }."}, 200)


@bp.route("/transfer-btc", methods=["POST"])
@use_kwargs(transfer_args)
def transfer_btc(amount, address, description="BTC Transfer", _type="transfer"):
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    db_response = mdb.get("merchants", mdb_query, {"_id": 0})
    merchant_id = mdb_query.get('merchant_id')

    db_response = db_response[0]
    balances = db_response.get("balances", {"usd": 0, "btc": 0})

    required_amount = amount * 1.01
    if balances.get("btc", 0) < required_amount:
        return responsify({"error": f"Insufficient BTC balance"}, 400)

    now = int(datetime.now().timestamp())
    label = f"{now}m{merchant_id}"

    transaction = {
        "type": _type,
        "description": description,
        "receiver": address,
        "btc_amount": amount,
        "on_hold": {
            "amount": required_amount,
            "currency": "btc"
        },
        "initiated_at": now,
        "transaction_label": label,
        "status": "pending",
        "merchant_id": merchant_id
    }

    email = db_response.get("email")
    otp = random.randrange(100000, 1000000)

    try:
        mailer.send({
            "email": email,
            "payload": {
                "otp": otp
            }
        })
    except Exception as e:
        logging.error(e)
        return responsify({"error": "Unable to send OTP to merchant's email"}, 400)

    inserted_id = mdb.add("transactions", transaction)
    rst._set(label, otp)

    response = {"token": str(inserted_id), "success": "OTP sent to mechant's email."}

    return responsify(response, 201)


@bp.route("/transfer/otp-confirm", methods=["POST"])
@use_kwargs({ **token_args, **otp_args})
def confirm_otp(token, otp):
    mdb_query = check_jwt_tokens(request)
    if "error" in mdb_query:
        return responsify(mdb_query, 401)

    merchant_id = mdb_query.get('merchant_id')

    transaction = mdb.get("transactions", {"_id": ObjectId(token)})
    if not transaction:
        return responsify({"error": "Invalid token."}, 400)
    transaction = transaction[0]

    if transaction.get("merchant_id") != merchant_id:
        return responsify({"error": "Incorrect token."}, 400)

    db_response = mdb.get("merchants", mdb_query, {"_id": 0})
    db_response = db_response[0]
    balances = db_response.get("balances", {"usd": 0, "btc": 0})
    on_hold = transaction.get("on_hold")
    if not on_hold:
        return responsify({"error": "Incorrect transaction."}, 400)

    transaction_label = transaction.get("transaction_label")

    _status = rst._get(transaction_label)
    if _status.get("error"):
        return responsify({"error": "Unable to confirm OTP."}, 400)

    status = _status.get("status")
    if not status or status == 'None':
        return responsify({"error": "Unable to confirm OTP."}, 400)

    if otp != status:
        return responsify("Invalid OTP.", 401)

    rst._del(transaction_label)

    status_code, content = btc_node.transfer(transaction.get("btc_amount"), transaction.get("receiver"))
    if status_code != 200:
        return responsify({"error": "Failed to transfer BTC"}, 500)

    transaction_id = content.get("result")
    blockExplorer = f"https://blockstream.info/testnet/tx/{transaction_id}"

    balances[on_hold["currency"]] -= on_hold["amount"]
    tx = {
        "updated_at": int(datetime.now().timestamp()),
        "status": "confirmed",
        "transaction_id": transaction_id,
        "blockExplorer": blockExplorer
    }

    mdb.alter("transactions", {"_id": ObjectId(token)}, tx, {"on_hold": 0})
    mdb.alter("merchants", mdb_query, {"balances": balances})

    return responsify({"success": f"Transferred { transaction.get('btc_amount') } BTC to { transaction.get('receiver') }."}, 200)

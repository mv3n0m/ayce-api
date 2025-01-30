import os
import time
from flask import request
from src.settings import btcdc, mailer, mdb
from src.utils import responsify
from src.utils.args_schema import contact_form_args, email_args
from src.utils.validations import validate_currency
from .handlers import create_blueprint

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


### Contact form routes
@route("/site/<form_type>", ["POST"], _args=contact_form_args, _auth=None)
def site_requests(*args, **kwargs):
    if kwargs.get("form_type") not in ["contact", "build"]:
        return responsify({"error": "Not found."}, 404)

    kwargs.update({"submitted_at": f"{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))} UTC"})

    mdb.add("enquiries", kwargs)

    try:
        data = {
            "mail_type": "contact",
            "name": "Admin",
            "email": os.environ.get("AYCE_INFO_EMAIL"),
            "payload": kwargs
        }
        mailer.send(data)
    except Exception as e:
        print(e)
        return responsify({"error": "Failed to send site contact request mail."}, 500)

    return responsify({"success": "Request submitted succesfully"}, 200)


@route("/site/newsletter", ["POST"], _args=email_args, _auth=None)
def site_newsletter(*args, **kwargs):
    kwargs.update({"requested_at": f"{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))} UTC"})

    mdb.add("newsletter_requests", kwargs)

    try:
        data = {
            "mail_type": "newsletter",
            "name": "Admin",
            "email": os.environ.get("AYCE_INFO_EMAIL"),
            "payload": kwargs
        }
        mailer.send(data)
    except Exception as e:
        print(e)
        return responsify({"error": "Failed to send site newsletter request mail."}, 500)

    return responsify({"success": "Request submitted succesfully"}, 200)




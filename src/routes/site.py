import os
import time
from flask import request
from src.settings import mailer, mdb
from src.utils import responsify
from src.utils.args_schema import contact_form_args, email_args
from .handlers import create_blueprint

bp, route = create_blueprint("site", __name__, "/site")

@route("/<form_type>", ["POST"], _args=contact_form_args, _auth=None)
def site_requests(*args, **kwargs):
    if kwargs.get("form_type") not in ["contact", "build"]:
        return responsify({"error": "Not found."}, 404)

    kwargs.update({"submitted_at": f'{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))} UTC'})

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


@route("/newsletter", ["POST"], _args=email_args, _auth=None)
def site_newsletter(*args, **kwargs):
    kwargs.update({"requested_at": f'{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))} UTC'})

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




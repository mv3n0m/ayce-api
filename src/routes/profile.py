from src.settings import mdb
from src.utils import responsify
from src.utils.args_schema import token_args, business_args, billing_args, representative_args, beneficial_args, profile_data_args
from .handlers.user import User
from .handlers import create_blueprint


bp, route = create_blueprint("user_profile", __name__, "/user/profile")


@route("/business-details", ["POST"], business_args)
def business_details(user_id, *args, **kwargs):
    mdb.alter("profile_data", {"user_id": user_id}, {"business_details": kwargs}, upsert=True)
    return responsify({"success": "Business details added successfully"}, 201)

@route("/settlement-billing", ["POST"], billing_args)
def settlement_billing(user_id, *args, **kwargs):
    mdb.alter("profile_data", {"user_id": user_id}, {"settlement_billing": kwargs}, upsert=True)
    return responsify({"success": "Settlement/Billing details added successfully"}, 201)

@route("/authorized-representative", ["POST"], representative_args)
def authorized_representative(user_id, *args, **kwargs):
    mdb.alter("profile_data", {"user_id": user_id}, {"authorized_representative": kwargs}, upsert=True)
    return responsify({"success": "Authorized representative details added successfully"}, 201)

## need to write a separate route for updating beneficial owners as they can be multiple
@route("/beneficial-owner", ["POST"], beneficial_args)
def beneficial_owner(user_id, *args, **kwargs):
    beneficial_owners = []
    kwargs["date_of_birth"] = str(kwargs.get("date_of_birth")).split("T")[0]

    record = mdb.get("profile_data", {"user_id": user_id}, {"_id": 0, "beneficial_owners": 1})
    if record:
        beneficial_owners = record.get("beneficial_owners", [])

    beneficial_owners.append(kwargs)

    mdb.alter("profile_data", {"user_id": user_id}, {"beneficial_owners": beneficial_owners}, upsert=True)
    return responsify({"success": "Beneficial owner details added successfully"}, 201)

@route("/submit-details-confirmation")
def submit_details_confimation(user_id):

    mdb.alter("profile_data", {"user_id": user_id}, {"confirmed": True}, upsert=True)
    return responsify({"success": "Confirmation submitted successfully"}, 200)

@route("/", ["GET"])
def get_profile_data(user_id, *args, **kwargs):
    record = mdb.get("profile_data", {"user_id": user_id}, {"_id": 0, "user_id": 0, "confirmed": 0})
    if not record:
        return responsify({"error": "No data available"}, 400)

    record = record[0]

    return responsify(record, 200)

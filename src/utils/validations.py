import re
from uuid import UUID
from bson import ObjectId
from webargs import ValidationError


def validate_account_type(account):
    options = ["personal", "business"]
    if account.lower() not in options:
        raise ValidationError(f"Invalid account type. Available options: {options}")


def validate_mode(mode):
    options = ["on-chain", "lightning"]

    if not (mode and mode.lower() in options):
        raise ValidationError(f"Not a valid mode. Available options { options }")


def validate_id(_id, ret=False):

    try :
        _id = ObjectId(_id)
        if ret:
            return _id
    except Exception as e:
        print(e)
        raise ValidationError("Invalid id")


def validate_token(token):
    try :
        _id = UUID(token)
    except Exception as e:
        print(e)
        raise ValidationError("Invalid token")


def validate_amount(amount):
    if amount <= 0:
        raise ValidationError("Amount must be more than 0")


def validate_currency(curr):
    options = ["btc", "usd"]
    if curr.lower() not in options:
        raise ValidationError(f"Invalid currency. Available options: {options}")


def validate_transfer_type(value):
    options = ["withdrawal", "deposit"]
    if value.lower() not in options:
        raise ValidationError(f"Invalid transfer type. Available options: {options}")


def validate_address(addr):
    pass

def validate_otp(otp):
    if len(otp) != 6:
        raise ValidationError("Invalid OTP length.")

    try:
        otp = int(otp)
    except:
        raise ValidationError("Invalid OTP content.")


def validate_invoice_item(item):
    if not item:
        raise ValidationError("Invalid invoice item.")

    keys = ["name", "quantity", "price"]
    if len(keys) != len(item) or not all((i in keys for i in item.keys())):
        raise ValidationError("Invalid/Insufficient invoice item attribute/s.")

    errors = []
    if not isinstance(item.get("name"), str):
        errors.append("Name must be of string type.")

    if not isinstance(item.get("quantity"), int):
        errors.append("Quantity must be of integer type.")

    if not isinstance(item.get("price"), (float, int)):
        errors.append("Price must be of number type.")

    if errors:
        raise ValidationError("Invalid invoice item detail/s:  {}".format('\n'.join([e for e in errors])))


def validate_due(due):
    if not due:
        raise ValidationError("Invalid total due values.")

    keys = ["currency", "amount"]
    if len(keys) != len(due) or not all((i in keys for i in due.keys())):
        raise ValidationError("Invalid/Insufficient total due attribute/s.")

    if not isinstance(due.get("currency"), str) or due["currency"] not in ["USD", "BTC"]:
        raise ValidationError("Invalid currency.")

    if not isinstance(due.get("amount"), (float, int)):
        raise ValidationError("Invalid amount value.")


def validate_payouts_record(record):
    if not record:
        raise ValidationError("Invalid payouts record.")

    keys = ["address", "amount", "currency", "source_wallet"]
    if len(keys) != len(record) - 1 or not all((i in record.keys() for i in keys)):
        raise ValidationError("Invalid/Insufficient payouts record attribute/s.")

    errors = []
    if not isinstance(record.get("address"), str):
        errors.append("Address must be of string type.")

    if not isinstance(record.get("amount"), (float, int)):
        errors.append("Amount must be of number type.")

    if not isinstance(record.get("currency"), str):
        errors.append("Currency must be of string type.")
    elif record.get("currency").lower() not in ["btc", "usd"]:
        errors.append("Invalid currency.")

    if not isinstance(record.get("source_wallet"), str):
        errors.append("Source wallet must be of string type.")
    elif record.get("source_wallet").lower() not in ["btc", "usd"]:
        errors.append("Invalid source_wallet.")

    if record.get("address_type"):
        if not isinstance(record.get("address_type"), str):
            errors.append("Address type must be of string type.")
        elif record.get("address_type").lower() not in ["email", "btc_onchain"]: #, "ayce_id", "btc_lightning"]:
            errors.append("Invalid address_type.")

    if errors:
        raise ValidationError("Invalid payouts detail/s:  {}".format('\n'.join([e for e in errors])))


def validate_collect_item(item):
    options = ["full_name", "email", "shipping_address", "phone_number"]

    if item not in options:
        raise ValidationError(f"Invalid collect item. Options: {options}")


def validate_price(price):

    if not all((k in ["amount", "currency"] for k in price.keys())):
        raise ValidationError("Invalid price attribute/s.")

    if price["amount"] <= 0:
        raise ValidationError("Amount must be more than 0")

    options = ["btc", "usd"]
    if price["currency"].lower() not in options:
        raise ValidationError(f"Invalid currency. Available options: {options}")


def validate_discount(discount):

    if not all((k in ["value", "unit"] for k in discount.keys())):
        raise ValidationError("Invalid discount attribute/s.")

    if discount["value"] <= 0:
        raise ValidationError("Discount value must be a positive number")

    if discount["unit"].lower() not in ["amt", "%"]:
        raise ValidationError(f"Invalid discount unit. Options: {['amt', '%']}")


def validate_permission(permission):
    options = ["read-only", "invoices", "withdrawals"]

    if permission not in options:
        raise ValidationError(f"Invalid permission type. Available options: {options}")


def validate_ip(ip):
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

    if not re.match(pattern, ip):
        raise ValidationError("Invalid IP address.")


def validate_url(url):
    pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    # pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*([?#][^\s]*)?$'
    if not re.match(pattern, url):
        raise ValidationError("Invalid URL.")


def validate_request_type(_type):
    options = ["charge", "withdrawal"]

    if _type not in options:
        raise ValidationError(f"Invalid request type. Available options: {options}")


def validate_request_status(status):
    options = ["processing", "confirmed", "failed", "refunded", "paid", "expired", "cancelled", "underpaid", "completed", "pending"]

    if status not in options:
        raise ValidationError(f"Invalid request status. Available options: {options}")


def validate_profile_data_field(field):
    options = ["business_details", "settlement_billing", "authorized_representative", "beneficial_owners"]

    if field not in options:
        raise ValidationError(f"Invalid account data field. Available options: {options}")
from webargs import fields, validate
from .validations import (
    validate_token,
    validate_mode,
    validate_due,
    validate_id,
    validate_amount,
    validate_currency,
    validate_transfer_type,
    validate_address,
    validate_otp,
    validate_invoice_item,
    validate_payouts_record,
    validate_price,
    validate_collect_item,
    validate_discount,
    validate_permission,
    validate_account_type,
    validate_ip,
    validate_url,
    validate_request_type,
    validate_request_status,
    validate_profile_data_field,
    validate_scheduled_transfers_period
)


wallet_name_args = {"wallet_name": fields.Str(required=True, validate=validate.Length(min=3))}

mode_args = {"mode": fields.Str(required=True, validate=validate_mode)}

wallet_transaction_args = {
    **wallet_name_args,
    **mode_args
}

transaction_args = {
    "amount": fields.Float(required=True, validate=validate_amount),
    "description": fields.Str(required=False, validate=validate.Length(min=3))
}

exchange_args = {
    "amount": fields.Float(required=True, validate=validate_amount),
    "_from": fields.Str(required=True, validate=validate_currency),
    "_to": fields.Str(required=True, validate=validate_currency)
}

transfer_args = {
    "amount": fields.Float(required=True, validate=validate_amount),
    "address": fields.Str(required=True, validate=validate_address),
    "description": fields.Str(required=False, validate=validate.Length(min=3)),
    "_type": fields.Str(required=False, validate=validate_transfer_type)
}

scheduled_transfers_options = ["daily", "weekly"]
scheduled_transfer_args = {
    "usd": fields.Str(required=False, validate=validate_scheduled_transfers_period),
    "btc": fields.Str(required=False, validate=validate_scheduled_transfers_period),
    "btc_address": fields.Str(required=False, validate=validate_address)
}

# pos_args = {
#     **mode_args,
#     "merchant_id": fields.Str(required=True),
#     "amount": fields.Float(required=True, validate=validate_amount)
# }

token_args = lambda key="token": {
    # revert to validation with a new validator lambda function that depends on the key
    # key: fields.Str(required=True, validate=validate_token)

    key: fields.Str(required=True)
}

otp_args = {
    "otp": fields.Str(required=True, validate=validate_otp)
}

token_otp_args = {
    **token_args(),
    **otp_args
}

email_args = {
    "email": fields.Email(required=True) # add email validation
}

password_args = {
    "password": fields.Str(required=True) # add password validation
}

account_type_args = {
    "account_type": fields.Str(required=False, default="business", validate=validate_account_type) # add validation and wherever required above
}

auth_args = {
    **email_args,
    **password_args,
    **account_type_args
}


user_info_args = {
    "id": fields.Int(default=0),
    "first_name": fields.Str(required=True),
    "last_name": fields.Str(required=True)
}

user_args = {
    "username": fields.Str(),
    "address": fields.Str(),
    "nationality": fields.Str(),
    "residency": fields.Str(),
    "registrationnumber": fields.Str(),
    "phonenumber": fields.Str(),
    "weaddress": fields.Str(),
    "productandservices": fields.Str(),
    "estimatedmonthlyprocessingvolume": fields.Str(),
    "avg_transaction_size": fields.Str()
}

confidential_args = {
    "emailaddress": fields.Email(required=True),
    "pswd": fields.Str(required=True)
}

email_args = {
    "email": fields.Email(required=True)
}

update_password_args = {
    "token": fields.Str(required=True),
    "password": fields.Str(required=True)
}

invoice_args = {
    "recipient_name": fields.Str(required=True),
    "recipient_email": fields.Email(required=True),
    "invoice_number": fields.Integer(required=True),
    "due_date": fields.DateTime("%Y-%m-%d", required=True),
    "invoice_items": fields.List(
        fields.Dict(keys=fields.Str, required=True, validate=validate_invoice_item),
        required=True, validate=validate.Length(min=1)),
    "total_due": fields.Dict(keys=fields.Str, required=True, validate=validate_due),
    "discount_percentage": fields.Float(required=False),
    "additional_information": fields.Dict(required=False)
}

payouts_args = {
    "records": fields.List(
        fields.Dict(keys=fields.Str, required=True, validate=validate_payouts_record),
        required=True, validate=validate.Length(min=1)),
    "notes": fields.Str(required=False)
}

payment_buttons_args = {
    "product": fields.Str(required=True),
    "description": fields.Str(required=False),
    "price": fields.Dict(keys=fields.Str, required=False, validate=validate_price),
    "image": fields.Str(required=False),
    "collectibles": fields.List(fields.Str(required=True, validate=validate_collect_item), required=False),
    "additional": fields.List(fields.Str(required=True), required=False),
    "success_url": fields.Str(required=False),
    "discount_code": fields.Str(required=False),
    "discount": fields.Dict(keys=fields.Str, required=False, validate=validate_discount)
}

payment_information_args = {
    "auto_conversion": fields.Bool(required=False),
    "split_settlement": fields.Float(required=False, validate=lambda x: x >= 0 and x <= 100),
    "native_currency": fields.Str(required=False, validate=validate_currency)
}
    # "settlement_account": fields.Str(required=False),


developer_key_args = {
    "label": fields.Str(required=True, validate=validate.Length(min=3)),
    "permission": fields.Str(required=True, validate=validate_permission),
    # "permissions": fields.List(fields.Str(required=True, validate=validate_permission), required=True), # maybe for later
    "ip_whitelist": fields.List(fields.Str(required=True, validate=validate_ip), required=False)
}

simulator_args = {
    "api_key": fields.Str(required=True, validate=validate_token),
    "callback_url": fields.Str(required=True, validate=validate_url),
    "type": fields.Str(required=True, validate=validate_request_type),
    "status": fields.Str(required=True, validate=validate_request_status)
}


address_args = lambda _country_key="country": {
    "address_1": fields.Str(required=True),
    "address_2": fields.Str(required=False),
    "city": fields.Str(required=True),
    "state": fields.Str(required=True),
    "zipcode": fields.Str(required=True),
    _country_key: fields.Str(required=True),
}

business_args = {
    "ownership_type": fields.Str(required=True),
    "legal_name": fields.Str(required=True),
    "phone_number": fields.Str(required=True),
    "email_address": fields.Str(required=True),
    **address_args("location"),
    "website_url": fields.Str(required=False),
    "product_and_services": fields.Str(required=False),
    "website_url": fields.Str(required=False, validate=validate_url),
    "estimated_monthly_processing_volume": fields.Str(required=False),
    "average_transaction_size": fields.Str(required=False),
    "registration_number": fields.Str(required=False),
}

business_documents_args = {
    "govt_issued_id": fields.List(fields.Str(required=True), required=True, validate=validate.Length(equal=2)),
    "proof_of_business": fields.List(fields.Str(required=True), required=True, validate=validate.Length(min=1)),
    "additional": fields.List(fields.Str(required=True), required=False, validate=validate.Length(min=1))
}

billing_args = {
    "account_name": fields.Str(required=True),
    "bank_name": fields.Str(required=True),
    "iban_or_swift": fields.Str(required=True),
    "routing_number": fields.Str(required=True),
    "account_number": fields.Str(required=True),
    "account_type": fields.Str(required=True),
    "currency": fields.Str(required=True)
}

representative_args = {
    "legal_name": fields.Str(required=True),
    "date_of_birth": fields.Date("%Y-%m-%d", required=True),
    "nationality": fields.Str(required=True),
    **address_args(),
    "id_type": fields.Str(required=True),
    "id_number": fields.Str(required=True)
}

beneficial_args = {
    **representative_args,
    "ownership_percentage": fields.Float(required=True, validate=lambda x: x >= 0 and x <= 100),
}

profile_data_args = {
    "fields": fields.List(fields.Str(required=False, validate=validate_profile_data_field), required=False)
}

currency_args = {
    "currency": fields.Str(required=False, default="usd", validate=validate_currency)
}


contact_form_args = {
    "name": fields.Str(required=True, validate=lambda x: len(x) > 1),
    **email_args,
    "message": fields.Str(required=True)
}

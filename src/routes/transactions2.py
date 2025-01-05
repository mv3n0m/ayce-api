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
from src.utils import responsify
from src.utils.args_schema import wallet_name_args, token_args, transaction_args, exchange_args, transfer_args, otp_args, invoice_args, payouts_args, payment_buttons_args
from .handlers import create_blueprint


bp, route = create_blueprint("transactions", __name__, "/transactions")

@route("/list", methods=["POST"])
def list_transactions(user, kwargs):
    return responsify({})

@route("/pos/create", methods=["POST"])
def create_pos(user, kwargs):
    return responsify({})

@route("/pos/update/<reference_id>", methods=["POST"])
def update_pos(user, kwargs):
    return responsify({})

@route("/invoice/create", methods=["POST"])
def create_invoice(user, kwargs):
    return responsify({})

@route("/invoice/update/<reference_id>", methods=["POST"])
def update_invoice(user, kwargs):
    return responsify({})

# @route("/payment/create", methods=["POST"])
# def create_pos(user, kwargs):
#     return responsify({})

# @route("/payment/update/<reference_id>", methods=["POST"])
# def create_pos(user, kwargs):
#     return responsify({})


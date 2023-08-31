import os
import logging
from dotenv import load_dotenv
from src.db.redis import Store
from src.services.btc import BTCNode
from src.db.mongo import MongoWrapper
from src.services.tokenize import Tokenize
from webargs.flaskparser import FlaskParser
from src.services.mail import SendGridMailer
from src.services.blockchaindotcom import BtcApi
from logging.handlers import TimedRotatingFileHandler

load_dotenv()


APP_SECRET = os.environ.get("APP_SECRET")
JWT_EXPIRY_DAYS = int(os.environ.get("JWT_EXPIRY_DAYS", 1))

if not os.path.exists("logs"):
    os.mkdir("logs")

log_handler = TimedRotatingFileHandler(filename="logs/btc_log",
                                       when="midnight",
                                       backupCount=10)

logging.basicConfig(
    format="%(asctime)-15s [%(levelname)s] %(name)-8s %(message)s",
    handlers=[log_handler],
    level=logging.INFO)

class Parser(FlaskParser):
    DEFAULT_VALIDATION_STATUS = 400

parser = Parser()
mailer = SendGridMailer()

rst = Store()
btcdc = BtcApi(rst)
mdb = MongoWrapper(os.environ.get("DB_NAME"), os.environ.get("MDB_URI"))
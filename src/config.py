import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

SWAGGER = {
    'swagger': "2.0",
    'title': '',
    'description': '',
    'uiversion': 3,
    'termsOfService': '',
    'version': '',
    'hide_top_bar': True,
    'favicon': "https://uploads-ssl.webflow.com/64d3ab3d262fca4024951cea/64d3bce14e061751094751f9_logo-color.svg",
    'head_text': '<div style="margin-top: 20px;display: flex;justify-content: center;"><img src="https://uploads-ssl.webflow.com/64d3ab3d262fca4024951cea/64d3bce14e061751094751f9_logo-color.svg" alt="logo"/></div>'
}

JWT_SECRET_KEY = os.environ.get("APP_SECRET")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.environ.get("JWT_EXPIRY_MINUTES", 10)))

MAIL_SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
MAIL_DEFAULT_SENDER = os.environ.get("DEFAULT_SENDER")

DB_NAME = os.environ.get("DB_NAME")
DB_URI = os.environ.get("DB_URI")
DB_CREDS = {
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT"),
    "username": os.environ.get("DB_USERNAME"),
    "password": os.environ.get("DB_PASSWORD")
}

AWS_REGION = os.environ.get("AWS_REGION")
AWS_KEY_ID = os.environ.get("AWS_KEY_ID")
AWS_KEY_SECRET = os.environ.get("AWS_KEY_SECRET")

LAMBDA_FUNCTION_NAME = os.environ.get("LAMBDA_FUNCTION_NAME")
LAMBDA_FUNCTION_URL = os.environ.get("LAMBDA_FUNCTION_URL")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

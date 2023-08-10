from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from flask_redis import FlaskRedis
from src.routes import blueprints
from src.settings import rst, mailer


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    redis = FlaskRedis(app)
    rst.init_store(redis)

    mailer.init_app(app)
    CORS(app)
    Swagger(app)

    for bp in blueprints:
        app.register_blueprint(bp)

    return app

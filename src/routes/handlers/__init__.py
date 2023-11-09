from flask import Blueprint
from src.settings import parser
from src.utils import responsify
from src.decorators import route_wrapper


def create_blueprint(bp_name, module_name, url_prefix=""):

    use_kwargs = parser.use_kwargs

    bp = Blueprint(bp_name, module_name, url_prefix=url_prefix)

    @bp.errorhandler(400)
    def handle_error(err):
        messages = err.data.get("messages", ["Invalid request."])
        return responsify({"errors": messages}, err.code)

    @bp.errorhandler(429)
    def handle_rate_limit_error(err):
        return responsify(
            {"error": "You have consumed your daily request quota."}, err.code)

    def route(*args, **kwargs):
        return route_wrapper(bp, use_kwargs, *args, **kwargs)

    return bp, route
from .handlers import create_blueprint
from src.handlers.transaction import Transaction

bp, route = create_blueprint("payments", __name__, "/payments")


@route("/test-route")
def test_route():
    data = Transaction.create({"test": 1}).as_dict()
    return {}
from .misc import bp as misc_bp
from .users import bp as users_bp
from .profile import bp as profile_bp
from .settings import bp as settings_bp
from .developers import bp as developers_bp
from .transactions import bp as transactions_bp

blueprints = [
    misc_bp,
    users_bp,
    profile_bp,
    settings_bp,
    developers_bp,
    transactions_bp,
]
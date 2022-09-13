# Extension for implementing Alembic database migrations
from flask_migrate import Migrate

# Extension for implementing SQLAlchemy ORM
from flask_sqlalchemy import SQLAlchemy

# Extension for implementing Flask-Login for authentication
from flask_login import LoginManager

# Extension for implementing translations
from flask_babel import Babel, _
from flask_babel import lazy_gettext as _l

db = SQLAlchemy()
babel = Babel()
login_manager = LoginManager()

def init_extensions(app):
    db.init_app(app)
    babel.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"
    login_manager.login_message = _l("You need to be logged in to access this page.")
    login_manager.login_message_category = "danger"
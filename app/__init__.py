# Imports from Flask
from flask import Flask

# Extension for implementing Alembic database migrations
from flask_migrate import Migrate

# Extension for implementing SQLAlchemy ORM
from flask_sqlalchemy import SQLAlchemy

# Extension for implementing Flask-Login for authentication
from flask_login import LoginManager

# Extension for implementing translations
from flask_babel import Babel, _
from flask_babel import lazy_gettext as _l

# Other imports
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or "prc9FWjeLYh_KsPGm0vJcg",
    SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(basedir, "globomantics.sqlite"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    IMAGE_UPLOADS=os.path.join(basedir, "uploads"),
    ALLOWED_IMAGE_EXTENSIONS=["jpeg", "jpg", "png"],
)

# Initializing extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
babel = Babel(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"
login_manager.login_message = _l("You need to be logged in to access this page.")
login_manager.login_message_category = "danger"

# Imports from subpackages (views)
from app.album.views import album
app.register_blueprint(album, url_prefix="/album")
from app.tour.views import tour
app.register_blueprint(tour, url_prefix="/tour")
from app.auth.views import auth
app.register_blueprint(auth)
from app.main.views import main
app.register_blueprint(main)


from app.main.views import page_not_found
app.register_error_handler(404, page_not_found)

# Date formatting Jinja2 filter
@app.template_filter("date_format")
def date_format(value, format="%m/%d/%Y"):
    return value.strftime(format)

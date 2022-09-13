# Imports from Flask
from flask import Flask

# Other imports
import os
import config
import re

# Import global extension variables
from app.extensions import *

basedir = os.path.abspath(os.path.dirname(__file__))
app_env = os.environ.get("FLASK_ENV")


def create_app(config_env=app_env):
    app = Flask(__name__)
    app.config.from_object("config.{}Config".format(config_env.capitalize()))

    # Initializing extensions
    init_extensions(app)

    # Language url prefix
    lang_list = ",".join(app.config["LANGUAGES"])
    lang_prefix = f"<any({lang_list}):lang>"

    # Imports from subpackages (views)
    with app.app_context():
        from app.album.views import album

        app.register_blueprint(album, url_prefix=f"/{lang_prefix}/album")

        from app.main.views import main

        app.register_blueprint(main, url_prefix=f"/{lang_prefix}")

    from app.tour.views import tour

    app.register_blueprint(tour, url_prefix=f"/{lang_prefix}/tour")

    from app.auth.views import auth

    app.register_blueprint(auth, url_prefix=f"/{lang_prefix}")

    from app.admin.views import admin

    app.register_blueprint(admin, url_prefix=f"/{lang_prefix}/admin")

    # resource links for admins
    app.config["ADMIN_VIEWS"] = [
        re.search("admin.(.*)_table", p).group(1)
        for p in list(app.view_functions.keys())
        if re.search("admin.(.*)_table", p)
    ]

    # Imports for errors pages
    from app.errors import page_not_found

    app.register_error_handler(404, page_not_found)

    # Imports for Jinja filters
    from app.filters import date_format

    app.add_template_filter(date_format)

    # Define URL processors
    from app.url_processors import url_processors
    app.register_blueprint(url_processors)

    return app

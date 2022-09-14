from app import create_app, db
from flask_migrate import Migrate
from cli import register_click_commands

app = create_app()
migrate = Migrate(app, db, render_as_batch=True)
register_click_commands(app)
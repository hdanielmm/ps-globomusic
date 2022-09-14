import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or "prc9FWjeLYh_KsPGm0vJcg"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS = ["jpeg", "jpg", "png"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_VIEWS = []
    LANGUAGES = ["en", "hr"]

CACHE_TYPE = "redis"
CACHE_REDIS_HOST = "localhost"
CACHE_REDIS_PORT = "6379"
CACHE_REDIS_DB = "0"

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "globomantics.sqlite")
    IMAGE_UPLOADS = os.path.join(basedir, "uploads")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "testing_db.sqlite")
    IMAGE_UPLOADS = os.path.join(basedir, "uploads")

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("FLASK_DB_URI") or "sqlite:///" + os.path.join(basedir, "globomantics.sqlite")
    IMAGE_UPLOADS = os.environ.get("FLASK_UPLOADS_FOLDER_URL") or os.path.join(basedir, "uploads")
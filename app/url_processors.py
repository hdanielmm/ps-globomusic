from flask import Blueprint, g, current_app

url_processors = Blueprint("url_processors", __name__)

@url_processors.app_url_value_preprocessor
def processor(endpoint, values):
    try:
        g.lang = values.pop("lang")
    except:
        g.lang = current_app.config["LANGUAGES"][0]

@url_processors.app_url_defaults
def add_language_code(endpoint, values):
    if "lang" in values:
        return
    if current_app.url_map.is_endpoint_expecting(endpoint, "lang"):
        values["lang"] = g.lang
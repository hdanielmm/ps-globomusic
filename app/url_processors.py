from flask import Blueprint, request, after_this_request, g, current_app

url_processors = Blueprint("url_processors", __name__)

@url_processors.before_app_request
def before_request():
    # Not really a URL processor, but we will still
    # put it her for convenience
    if request.endpoint is "static":
        return
    if request.cookies.get("lang") != g.lang:
        @after_this_request
        def set_cookie(response):
            response. set_cookie("lang", g.lang, max_age=60*60*24*100)
            return response

@url_processors.app_url_value_preprocessor
def processor(endpoint, values):
    try:
        if endpoint is "static":
            return
        g.lang = values.pop("lang")
    except:
        if (
            request.cookies.get("lang") and
            request.cookies.get("lang") in current_app.config["LANGUAGES"]
        ):
            g.lang = request.cookies.get("lang")
        else:
            g.lang = current_app.config["LANGUAGES"][0]

@url_processors.app_url_defaults
def add_language_code(endpoint, values):
    if "lang" in values:
        return
    if current_app.url_map.is_endpoint_expecting(endpoint, "lang"):
        values["lang"] = g.lang
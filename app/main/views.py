# Imports from Flask
from flask import render_template

# Imports from the app package
from app import app

# Home route
@app.route("/")
def home():
    return render_template("home.html")


# Date formatting Jinja2 filter
@app.template_filter("date_format")
def date_format(value, format="%m/%d/%Y"):
    return value.strftime(format)


# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html")

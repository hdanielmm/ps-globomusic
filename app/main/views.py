# Imports from Flask
from flask import Blueprint, current_app, redirect, render_template, url_for
from flask_login import current_user
from app import cache

main = Blueprint("main", __name__, template_folder="templates")

def root():
    return redirect(url_for("main.home"))

# Home route
@main.route("/")
@cache.cached(timeout=180, unless=lambda: current_user.is_authenticated)
def home():
    # print("Home page is rendered")
    return render_template("home.html")

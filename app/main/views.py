# Imports from Flask
from flask import Blueprint, current_app, render_template


main = Blueprint("main", __name__, template_folder="templates")

# Home route
@main.route("/")
def home():
    return render_template("home.html")

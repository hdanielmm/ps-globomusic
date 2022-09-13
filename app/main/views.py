# Imports from Flask
from flask import Blueprint, current_app, redirect, render_template, url_for


main = Blueprint("main", __name__, template_folder="templates")

def root():
    return redirect(url_for("main.home"))

# Home route
@main.route("/")
def home():
    return render_template("home.html")

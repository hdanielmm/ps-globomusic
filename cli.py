import click
import os
import re
from flask import current_app
from flask.cli import with_appcontext
from app import db
from app.models import User


@click.command("test")
def test():
    os.system("python3 test.py -v")


@click.command("list-bp-endpoints")
@click.argument("blueprint")
@with_appcontext
def list_bp_endpoints(blueprint):
    """This command lists all of the endpoints of the given blueprint"""
    for endpoint in current_app.view_functions.keys():
        if re.search(f"^{blueprint}.", endpoint):
            click.echo(endpoint)


@click.group("user")
def user():
    pass


@user.command("create")
@click.option(
    "-u", "--username", prompt="Username", help="Users username", required=True
)
@click.option("-e", "--email", prompt="Email", help="Users email", required=True)
@click.option(
    "-p",
    "--password",
    hide_input=True,
    prompt="Password",
    default="password123",
    help="Users password",
)
@click.option(
    "-a",
    "--admin",
    is_flag=True,
    help="It turns the new user into an admin",
    prompt="Is this user an admin?",
)
@with_appcontext
def create(username, email, password, admin):
    """Command for creating new users inside of the globomantics database"""
    user = User.query.filter_by(username=username).first()
    if user:
        click.echo("A user already exists with that username. Choose another one.")
        return
    user = User.query.filter_by(email=email).first()
    if user:
        click.echo("A user already exists with that email. Choose another one.")
        return

    user = User(username, email, password)
    if admin:
        user.make_admin()
    try:
        db.session.add(user)
        db.session.commit()
        click.echo(
            "User {} has been successfully saved to the database.".format(username)
        )
    except Exception as e:
        click.echo("Something went wrong.")
        click.echo(e)
        db.session.rollback()


def register_click_commands(app):
    app.cli.add_command(test)
    app.cli.add_command(list_bp_endpoints)
    app.cli.add_command(user)

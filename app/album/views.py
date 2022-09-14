# Imports from Flask
from flask import abort, Blueprint, current_app, flash, redirect, render_template, send_from_directory, url_for

# Extension for implementing Flask-Login for authentication
from flask_login import current_user, login_required

# Extension for implementing translations
from flask_babel import _
from flask_babel import lazy_gettext as _l

# Methods for generating tokens
from secrets import token_hex

# Methods from Werkzeug for managing password hashing and sanitizing filenames
from werkzeug.utils import secure_filename

# Other imports
import os
import datetime
from app.album.forms import CreateAlbumForm, UpdateAlbumForm

# Imports from app package
from app import db, cache
from app.models import Album
from sqlalchemy.orm import joinedload

album = Blueprint("album", __name__, template_folder="templates")

@cache.cached(timeout=60, key_prefix="list_of_albums")
def get_albums():
    # print("Gretting albums from the database")
    return Album.query.options(joinedload(Album.user)).all()

# Route for listing albums
@album.route("/")
@login_required
def list():
    albums = get_albums()
    return render_template("list_albums.html", albums=albums)


# Route for creating new albums
@album.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = CreateAlbumForm()

    if form.validate_on_submit():
        title = form.title.data
        artist = form.artist.data
        description = form.description.data
        genre = form.genre.data
        image = save_image_upload(form.image)
        release_date = form.release_date.data

        album = Album(
            title, artist, description, genre, image, release_date, current_user.id
        )
        db.session.add(album)
        db.session.commit()
        flash(_("The new album has been added."), "success")
        return redirect(url_for("album.show", slug=album.slug))

    return render_template("create_album.html", form=form)


# Route for updating an album
@album.route("/edit/<slug>", methods=["GET", "POST"])
@login_required
def edit(slug):
    form = UpdateAlbumForm()

    album = Album.query.filter_by(slug=slug).first()

    if not album or not current_user.is_album_owner(album):
        flash(_("You are not authorized to do this."), "danger")
        return redirect(url_for("main.home"))

    if form.validate_on_submit():
        title = form.title.data
        artist = form.artist.data
        description = form.description.data
        genre = form.genre.data

        album.title = title
        album.artist = artist
        album.description = description
        album.genre = genre

        db.session.add(album)
        db.session.commit()
        flash(_("The album has been updated."), "success")
        return redirect(url_for("album.show", slug=album.slug))

    form.title.data = album.title
    form.artist.data = album.artist
    form.description.data = album.description
    form.genre.data = album.genre
    return render_template("edit_album.html", album=album, form=form)


# Route for deleting an album
@album.route("/delete/<slug>", methods=["POST"])
@login_required
def delete(slug):
    album = Album.query.filter_by(slug=slug).first()
    if not album or not current_user.is_album_owner(album):
        flash("You are not authorized to do this.", "danger")
        return redirect(url_for("main.home"))
    db.session.delete(album)
    db.session.commit()
    flash(_("The album has been deleted."), "success")
    return redirect(url_for("main.home"))


# Route for showing an album
@album.route("/show/<slug>")
@login_required
def show(slug):
    album = Album.query.filter_by(slug=slug).first()
    if not album:
        abort(404)
    return render_template("show_album.html", album=album)


# Route for showing the uploaded images
@album.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(current_app.config["IMAGE_UPLOADS"], filename)


# Method for saving an uploaded image to the uploads directory
def save_image_upload(image):
    format = "%Y%m%dT%H%M%S"
    now = datetime.datetime.utcnow().strftime(format)
    random_string = token_hex(2)
    filename = random_string + "_" + now + "_" + image.data.filename
    filename = secure_filename(filename)
    image.data.save(os.path.join(current_app.config["IMAGE_UPLOADS"], filename))
    return filename

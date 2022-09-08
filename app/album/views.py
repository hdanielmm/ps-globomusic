# Imports from Flask
from flask import render_template, send_from_directory, flash, abort, url_for, redirect

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
from app import app, db
from app.models import Album

# Route for listing albums
@app.route("/album")
@login_required
def list_albums():
    albums = Album.query.all()
    return render_template("list_albums.html", albums=albums)


# Route for creating new albums
@app.route("/album/create", methods=["GET", "POST"])
@login_required
def create_album():
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
        return redirect(url_for("show_album", slug=album.slug))

    return render_template("create_album.html", form=form)


# Route for updating an album
@app.route("/album/edit/<slug>", methods=["GET", "POST"])
@login_required
def edit_album(slug):
    form = UpdateAlbumForm()

    album = Album.query.filter_by(slug=slug).first()

    if not album or not current_user.is_album_owner(album):
        flash(_("You are not authorized to do this."), "danger")
        return redirect(url_for("home"))

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
        return redirect(url_for("show_album", slug=album.slug))

    form.title.data = album.title
    form.artist.data = album.artist
    form.description.data = album.description
    form.genre.data = album.genre
    return render_template("edit_album.html", album=album, form=form)


# Route for deleting an album
@app.route("/album/delete/<slug>", methods=["POST"])
@login_required
def delete_album(slug):
    album = Album.query.filter_by(slug=slug).first()
    if not album or not current_user.is_album_owner(album):
        flash("You are not authorized to do this.", "danger")
        return redirect(url_for("home"))
    db.session.delete(album)
    db.session.commit()
    flash(_("The album has been deleted."), "success")
    return redirect(url_for("home"))


# Route for showing an album
@app.route("/album/show/<slug>")
@login_required
def show_album(slug):
    album = Album.query.filter_by(slug=slug).first()
    if not album:
        abort(404)
    return render_template("show_album.html", album=album)


# Route for showing the uploaded images
@app.route("/album/uploads/<filename>")
def uploads(filename):
    return send_from_directory(app.config["IMAGE_UPLOADS"], filename)


# Method for saving an uploaded image to the uploads directory
def save_image_upload(image):
    format = "%Y%m%dT%H%M%S"
    now = datetime.datetime.utcnow().strftime(format)
    random_string = token_hex(2)
    filename = random_string + "_" + now + "_" + image.data.filename
    filename = secure_filename(filename)
    image.data.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
    return filename

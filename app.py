# Imports from Flask
from flask import Flask, render_template, send_from_directory, flash, abort, url_for, redirect
# Extension for implementing Alembic database migrations
from flask_migrate import Migrate
# Extension for implementing SQLAlchemy ORM
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
# Extension for implementing Flask-Login for authentication
from flask_login import LoginManager, current_user, login_required, UserMixin, login_user, logout_user
# Extension for implementing WTForms for managing web forms
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.fields import StringField, SubmitField, TextAreaField, FileField, PasswordField, BooleanField
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import InputRequired, DataRequired, Length, ValidationError, Email, EqualTo
# Extension for implementing translations
from flask_babel import Babel, _
from flask_babel import lazy_gettext as _l
# Methods for generating tokens
from secrets import token_hex, token_urlsafe
# Methods from Werkzeug for managing password hashing and sanitizing filenames
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
# Package for creating slugs
from slugify import slugify
# Other imports
import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or "prc9FWjeLYh_KsPGm0vJcg",
    SQLALCHEMY_DATABASE_URI="sqlite:///"+ os.path.join(basedir, "globomantics.sqlite"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAX_CONTENT_LENGTH=16*1024*1024,
    IMAGE_UPLOADS=os.path.join(basedir, "uploads"),
    ALLOWED_IMAGE_EXTENSIONS=["jpeg", "jpg", "png"]
)

# Initializing extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
babel = Babel(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"
login_manager.login_message = _l("You need to be logged in to access this page.")
login_manager.login_message_category = "danger"

# Album SQLAlchemy model
class Album(db.Model):
    __tablename__ = "albums"

    id           = db.Column(db.Integer(), primary_key=True)
    title        = db.Column(db.String(255), nullable=False)
    artist       = db.Column(db.String(255), nullable=False)
    description  = db.Column(db.Text(), nullable=False)
    genre        = db.Column(db.String(255), nullable=False)
    image        = db.Column(db.Text(), nullable=False)
    release_date = db.Column(db.DateTime(), nullable=False)
    user_id      = db.Column(db.Integer(), db.ForeignKey("users.id"), index=True, nullable=False)
    slug         = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, title, artist, description, genre, image, release_date, user_id):
        self.title         = title
        self.artist        = artist
        self.description   = description
        self.genre         = genre
        self.image         = image
        self.release_date  = release_date
        self.user_id       = user_id

# Tour SQLAlchemy model
class Tour(db.Model):
    __tablename__ = "tours"

    id           = db.Column(db.Integer(), primary_key=True)
    title        = db.Column(db.String(255), nullable=False)
    artist       = db.Column(db.String(255), nullable=False)
    description  = db.Column(db.Text(), nullable=False)
    genre        = db.Column(db.String(255), nullable=False)
    start_date   = db.Column(db.DateTime(), nullable=False)
    end_date     = db.Column(db.DateTime(), nullable=False)
    user_id      = db.Column(db.Integer(), db.ForeignKey("users.id"), index=True, nullable=False)
    slug         = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, title, artist, description, genre, start_date, end_date, user_id):
        self.title         = title
        self.artist        = artist
        self.description   = description
        self.genre         = genre
        self.start_date    = start_date
        self.end_date      = end_date
        self.user_id       = user_id

# Method for updating slugs on title update
def update_slug(target, value, old_value, initiator):
    target.slug = slugify(value) + "-" + token_urlsafe(3)

event.listen(Album.title, "set", update_slug)
event.listen(Tour.title, "set", update_slug)

# User SQLAlchemy model
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id                 = db.Column(db.Integer(), primary_key=True)
    username           = db.Column(db.String(64), unique=True, nullable=False)
    email              = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash      = db.Column(db.String(255), nullable=False)
    albums             = db.relationship("Album", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    tours              = db.relationship("Tour", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def __init__(self, username="", email="", password=""):
        self.username         = username
        self.email            = email
        self.password_hash    = generate_password_hash(password)

    def __repr__(self):
        return "<User %r>" % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_album_owner(self, album):
        return self.id == album.user_id

    def is_tour_owner(self, tour):
        return self.id == tour.user_id

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

# General Album form
class AlbumForm(FlaskForm):
	title			= StringField(_l("Title"),
								validators=[
									InputRequired("Input is required!"),
									DataRequired("Data is required!"),
									Length(min=5, max=80, message="Title must be between 5 and 80 characters long")
								])
	artist			= StringField(_l("Artist"),
								validators=[
									InputRequired("Input is required!"),
									DataRequired("Data is required!"),
									Length(min=2, max=30, message="Artist name must be between 2 and 30 characters long")
								])
	description 	= TextAreaField(_l("Description"),
								validators=[
									InputRequired("Input is required!"),
									DataRequired("Data is required!"),
									Length(min=10, max=200, message="Description must be between 10 and 200 characters long")
								])
	genre			= StringField(_l("Genre"),
								validators=[
									InputRequired("Input is required!"),
									DataRequired("Data is required!"),
									Length(min=2, max=20, message="Genre must be between 2 and 20 characters long")
								])

# Form for creating albums
class CreateAlbumForm(AlbumForm):
	release_date	= DateField(_l("Release date"),
								validators=[
									InputRequired("Input is required!"),
									DataRequired("Data is required!")
								],
								format="%Y-%m-%d"
								)
	image		= FileField(_l("Album cover"),
								validators=[
									FileAllowed(app.config["ALLOWED_IMAGE_EXTENSIONS"], "Images only!"),
									FileRequired()
								])
	submit 		= SubmitField(_l("Upload album"))

# Form for updating albums
class UpdateAlbumForm(AlbumForm):
	submit 		= SubmitField(_l("Update album information"))

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
        title        = form.title.data
        artist       = form.artist.data
        description  = form.description.data
        genre        = form.genre.data
        image        = save_image_upload(form.image)
        release_date = form.release_date.data

        album = Album(title, artist, description, genre, image, release_date, current_user.id)
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
        title       = form.title.data
        artist      = form.artist.data
        description = form.description.data
        genre       = form.genre.data

        album.title       = title
        album.artist      = artist
        album.description = description
        album.genre       = genre

        db.session.add(album)
        db.session.commit()
        flash(_("The album has been updated."), "success")
        return redirect(url_for("show_album", slug=album.slug))

    form.title.data       = album.title
    form.artist.data      = album.artist
    form.description.data = album.description
    form.genre.data       = album.genre
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

# Form for user registration
class RegistrationForm(FlaskForm):
    username         = StringField(_l("Username *"),
                                validators=[
                                    InputRequired("Input is required!"),
                                    DataRequired("Data is required!"),
                                    Length(min=5, max=20, message="Username must be between 5 and 20 characters long")
                                ])
    email            = EmailField(_l("Email *"),
                                validators=[
                                    InputRequired("Input is required!"),
                                    DataRequired("Data is required!"),
                                    Length(min=10, max=30, message="Email must be between 5 and 30 characters long"),
                                    Email("You did not enter a valid email!")
                                ])
    password         = PasswordField(_l("Password *"),
                                validators=[
                                    InputRequired("Input is required!"),
                                    DataRequired("Data is required!"),
                                    Length(min=10, max=40, message="Password must be between 10 and 40 characters long"),
                                    EqualTo("password_confirm", message="Passwords must match")
                                ])
    password_confirm = PasswordField(_l("Confirm Password *"),
                                validators=[
                                    InputRequired("Input is required!"),
                                    DataRequired("Data is required!")
                                ])
    submit           = SubmitField(_l("Register"))

    def validate_username(form, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError("Username already exists.")

    def validate_email(form, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError("Email already exists.")

class LoginForm(FlaskForm):
    email        = EmailField(_l("Email"),
                                validators=[
                                    InputRequired("Input is required!"),
                                    DataRequired("Data is required!"),
                                    Length(min=10, max=30, message="Email must be between 5 and 30 characters long")
                                ])
    password     = PasswordField(_l("Password"),
                                validators=[
                                    InputRequired("Input is required!"),
                                    DataRequired("Data is required!"),
                                    Length(min=10, max=40, message="Password must be between 10 and 40 characters long")
                                ])
    remember_me  = BooleanField(_l("Remember me"))
    submit       = SubmitField(_l("Login"))

    def validate_email(form, field):
        user = User.query.filter_by(email=field.data).first()
        if user is None:
            raise ValidationError("This email is not registered.")

# Route for registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()

    if form.validate_on_submit():
        username    = form.username.data
        email       = form.email.data
        password    = form.password.data

        user = User(username, email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(_("You are registered."), "success")
        login_user(user)
        return redirect(url_for("home"))

    return render_template("register.html", form=form)

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid username or password"))
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("home"))

    return render_template("login.html", form=form)

# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# General Tour form
class TourForm(FlaskForm):
	title			= StringField(_l("Title"),
								validators=[
									InputRequired("Input is required!"),
									DataRequired("Data is required!"),
									Length(min=5, max=80, message="Title must be between 5 and 80 characters long")
								])
	artist			= StringField(_l("Artist"),
								validators=[
									InputRequired("Input is required!"),
									DataRequired("Data is required!"),
									Length(min=2, max=30, message="Artist name must be between 2 and 30 characters long")
								])
	description 	= TextAreaField(_l("Description"),
								validators=[
									InputRequired("Input is required!"),
									DataRequired("Data is required!"),
									Length(min=10, max=200, message="Description must be between 10 and 200 characters long")
								])
	genre			= StringField(_l("Genre"),
								validators=[
									InputRequired("Input is required!"),
									DataRequired("Data is required!"),
									Length(min=2, max=20, message="Genre must be between 2 and 20 characters long")
								])
	start_date		= DateField(_l("Start date"),
								validators=[
									InputRequired("Input is required!"),
									DataRequired("Data is required!")
								],
								format="%Y-%m-%d"
								)
	end_date		= DateField(_l("End date"),
								validators=[
									InputRequired("Input is required!"),
									DataRequired("Data is required!")
								],
								format="%Y-%m-%d"
								)

	def validate_start_date(form, field):
		if(field.data > form.end_date.data):
			raise ValidationError("Start date needs to be before the end date.")

# Form for creating new tours
class CreateTourForm(TourForm):
	submit 		= SubmitField(_l("Upload tour"))

# Form for updating a tour
class UpdateTourForm(TourForm):
	submit 		= SubmitField(_l("Update tour information"))

# Route for listing tours
@app.route("/tour")
@login_required
def list_tours():
    tours = Tour.query.all()
    return render_template("list_tours.html", tours=tours)

# Route for creating new tours
@app.route("/tour/create", methods=["GET", "POST"])
@login_required
def create_tour():
    form = CreateTourForm()

    if form.validate_on_submit():
        title        = form.title.data
        artist       = form.artist.data
        description  = form.description.data
        genre        = form.genre.data
        start_date   = form.start_date.data
        end_date     = form.end_date.data

        tour = Tour(title, artist, description, genre, start_date, end_date, current_user.id)
        db.session.add(tour)
        db.session.commit()
        flash(_("The new tour has been added."), "success")
        return redirect(url_for("show_tour", slug=tour.slug))

    return render_template("create_tour.html", form=form)

# Route for updating a tour
@app.route("/tour/edit/<slug>", methods=["GET", "POST"])
@login_required
def edit_tour(slug):
    form = UpdateTourForm()

    tour = Tour.query.filter_by(slug=slug).first()

    if not tour or not current_user.is_tour_owner(tour):
        flash(_("You are not authorized to do this."), "danger")
        return redirect(url_for("home"))

    if form.validate_on_submit():
        title       = form.title.data
        artist      = form.artist.data
        description = form.description.data
        genre       = form.genre.data
        start_date  = form.start_date.data
        end_date    = form.end_date.data

        tour.title       = title
        tour.artist      = artist
        tour.description = description
        tour.genre       = genre
        tour.start_date  = start_date
        tour.end_date    = end_date

        db.session.add(tour)
        db.session.commit()
        flash(_("The tour has been updated."), "success")
        return redirect(url_for("show_tour", slug=tour.slug))

    form.title.data       = tour.title
    form.artist.data      = tour.artist
    form.description.data = tour.description
    form.genre.data       = tour.genre
    form.start_date.data  = tour.start_date
    form.end_date.data    = tour.end_date
    return render_template("edit_tour.html", tour=tour, form=form)

# Route for deleting a tour
@app.route("/tour/delete/<slug>", methods=["POST"])
@login_required
def delete_tour(slug):
    tour = Tour.query.filter_by(slug=slug).first()
    if not tour or not current_user.is_tour_owner(tour):
        flash(_("You are not authorized to do this."), "danger")
        return redirect(url_for("home"))
    db.session.delete(tour)
    db.session.commit()
    flash(_("The tour has been deleted."), "success")
    return redirect(url_for("home"))

# Route for showing a tour
@app.route("/tour/show/<slug>")
@login_required
def show_tour(slug):
    tour = Tour.query.filter_by(slug=slug).first()
    if not tour:
        abort(404)
    return render_template("show_tour.html", tour=tour)

# Extension for implementing WTForms for managing web forms
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.fields import StringField, SubmitField, TextAreaField, FileField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, DataRequired, Length

# Extension for implementing translations
from flask_babel import lazy_gettext as _l

# Imports from the app package
from app import app

# General Album form
class AlbumForm(FlaskForm):
    title = StringField(
        _l("Title"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
            Length(
                min=5, max=80, message="Title must be between 5 and 80 characters long"
            ),
        ],
    )
    artist = StringField(
        _l("Artist"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
            Length(
                min=2,
                max=30,
                message="Artist name must be between 2 and 30 characters long",
            ),
        ],
    )
    description = TextAreaField(
        _l("Description"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
            Length(
                min=10,
                max=200,
                message="Description must be between 10 and 200 characters long",
            ),
        ],
    )
    genre = StringField(
        _l("Genre"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
            Length(
                min=2, max=20, message="Genre must be between 2 and 20 characters long"
            ),
        ],
    )


# Form for creating albums
class CreateAlbumForm(AlbumForm):
    release_date = DateField(
        _l("Release date"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
        ],
        format="%Y-%m-%d",
    )
    image = FileField(
        _l("Album cover"),
        validators=[
            FileAllowed(app.config["ALLOWED_IMAGE_EXTENSIONS"], "Images only!"),
            FileRequired(),
        ],
    )
    submit = SubmitField(_l("Upload album"))


# Form for updating albums
class UpdateAlbumForm(AlbumForm):
    submit = SubmitField(_l("Update album information"))

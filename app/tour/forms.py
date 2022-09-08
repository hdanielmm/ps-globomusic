# Extension for implementing WTForms for managing web forms
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, TextAreaField, FileField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, DataRequired, Length, ValidationError

# Extension for implementing translations
from flask_babel import lazy_gettext as _l

# General Tour form
class TourForm(FlaskForm):
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
    start_date = DateField(
        _l("Start date"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
        ],
        format="%Y-%m-%d",
    )
    end_date = DateField(
        _l("End date"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
        ],
        format="%Y-%m-%d",
    )

    def validate_start_date(form, field):
        if field.data > form.end_date.data:
            raise ValidationError("Start date needs to be before the end date.")


# Form for creating new tours
class CreateTourForm(TourForm):
    submit = SubmitField(_l("Upload tour"))


# Form for updating a tour
class UpdateTourForm(TourForm):
    submit = SubmitField(_l("Update tour information"))

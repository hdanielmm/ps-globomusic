# Extension for implementing WTForms for managing web forms
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    InputRequired,
    DataRequired,
    Length,
    ValidationError,
    Email,
    EqualTo,
)

# Extension for implementing translations
from flask_babel import lazy_gettext as _l

from app.models import User

# Form for user registration
class RegistrationForm(FlaskForm):
    username = StringField(
        _l("Username *"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
            Length(
                min=5,
                max=20,
                message="Username must be between 5 and 20 characters long",
            ),
        ],
    )
    email = EmailField(
        _l("Email *"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
            Length(
                min=10, max=30, message="Email must be between 5 and 30 characters long"
            ),
            Email("You did not enter a valid email!"),
        ],
    )
    password = PasswordField(
        _l("Password *"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
            Length(
                min=10,
                max=40,
                message="Password must be between 10 and 40 characters long",
            ),
            EqualTo("password_confirm", message="Passwords must match"),
        ],
    )
    password_confirm = PasswordField(
        _l("Confirm Password *"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
        ],
    )
    submit = SubmitField(_l("Register"))

    def validate_username(form, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError("Username already exists.")

    def validate_email(form, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError("Email already exists.")


class LoginForm(FlaskForm):
    email = EmailField(
        _l("Email"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
            Length(
                min=10, max=30, message="Email must be between 5 and 30 characters long"
            ),
        ],
    )
    password = PasswordField(
        _l("Password"),
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required!"),
            Length(
                min=10,
                max=40,
                message="Password must be between 10 and 40 characters long",
            ),
        ],
    )
    remember_me = BooleanField(_l("Remember me"))
    submit = SubmitField(_l("Login"))

    def validate_email(form, field):
        user = User.query.filter_by(email=field.data).first()
        if user is None:
            raise ValidationError("This email is not registered.")

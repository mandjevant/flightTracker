from flask_wtf import FlaskForm
from flask import flash
from flask_login import current_user
from wtforms import StringField, SubmitField, DateField, PasswordField, BooleanField
from wtforms.validators import DataRequired, ValidationError
from app.models import User
import datetime


class NotEqualTo(object):
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext(f"Invalid field name {self.fieldname}."))

        if field.data == other.data:
            flash("Current password and new password must not be identical.")
            raise ValidationError("Passwords are identical.")


class ValidateOldPassword(object):
    def __call__(self, form, field):
        user = User.query.filter_by(username=current_user.username).first()
        if not user.check_password(field.data):
            flash("Wrong current password.")
            raise ValidationError("Wrong current password.")


class ValidateAdmin(object):
    def __init__(self, is_admin: bool = True, message: str = "User is already an admin."):
        self.is_admin = is_admin
        self.message = message

    def __call__(self, form, field):
        user = User.query.filter_by(username=field.data).first()
        if user is None:
            return

        if user.is_admin() == self.is_admin:
            flash(self.message)
            raise ValidationError(self.message)


class ValidateUsername(object):
    def __init__(self, message: str = "User does not exist", new_user: bool = False):
        self.message = message
        self.new_user = new_user

    def __call__(self, form, field):
        user = User.query.filter_by(username=field.data).first()
        if (self.new_user and user is not None) or (not self.new_user and user is None):
            flash(self.message)
            raise ValidationError(self.message)


class addFlightForm(FlaskForm):
    callSign = StringField(label="Call sign",
                           validators=[DataRequired()],
                           description="Add a flight",
                           default="Call sign...",
                           render_kw={"onfocus": "this.value=''"})
    date = DateField(label="Date of flight",
                     validators=[DataRequired()],
                     description="Enter date of flight",
                     default=datetime.date.today,
                     format="%Y-%m-%d")
    flightFrom = StringField(label="From airport",
                             description="Enter departure airport",
                             default="Birmingham",
                             render_kw={"onfocus": "this.value=''"})
    flightTo = StringField(label="Destination airport",
                           description="Enter arrival airport",
                           default="Destination...",
                           render_kw={"onfocus": "this.value=''"})
    aircraft = StringField(label="Aircraft",
                           description="Type of aircraft",
                           default="Boeing 737-800")
    submit = SubmitField("Add flight")


class searchFlightForm(FlaskForm):
    callSign = StringField(label="Call sign",
                           validators=[DataRequired()],
                           description="Add a flight",
                           default="Call sign...",
                           render_kw={"onfocus": "this.value=''"})
    date = DateField(label="Date of flight",
                     validators=[DataRequired()],
                     description="Enter date of flight",
                     default=datetime.date.today,
                     format="%Y-%m-%d")
    submit = SubmitField("Search flight")


class editFlightForm(FlaskForm):
    flightFrom = StringField(label="From airport",
                             description="Enter departure airport")
    flightTo = StringField(label="Destination airport",
                           description="Enter arrival airport")
    aircraft = StringField(label="Aircraft",
                           description="Type of aircraft",
                           default="Boeing 737-800")
    submit = SubmitField("Edit flight")


class removeFlightForm(FlaskForm):
    callSign = StringField("Call sign",
                           validators=[DataRequired()],
                           description="Remove a flight",
                           default="Call sign...",
                           render_kw={"onfocus": "this.value=''"})
    date = DateField(label="Date of flight",
                     validators=[DataRequired()],
                     description="Enter date of flight",
                     default=datetime.date.today,
                     format="%Y-%m-%d")
    submit = SubmitField("Remove flight")


class addUserForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired(),
                                       ValidateUsername(message="User already exists. "
                                                                "Please use a different username.",
                                                        new_user=True)],
                           description="New Username",
                           default="Username",
                           render_kw={"onfocus": "this.value=''"})
    is_admin = BooleanField("Admin",
                            default=False)
    submit = SubmitField("Add user")


class upgradeUserForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired(), ValidateUsername(), ValidateAdmin()],
                           description="Username",
                           default="Username",
                           render_kw={"onfocus": "this.value=''"})
    submit = SubmitField("Upgrade user")


class downgradeUserForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired(), ValidateUsername(),
                                       ValidateAdmin(is_admin=False, message="User is not an admin.")],
                           description="Username",
                           default="Username",
                           render_kw={"onfocus": "this.value=''"})
    submit = SubmitField("Downgrade user")


class removeUserForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired(), ValidateUsername()],
                           description="Remove Username",
                           default="Username",
                           render_kw={"onfocus": "this.value=''"})
    submit = SubmitField("Remove user")


class loginForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired()],
                           description="Username")
    password = PasswordField("Password",
                             validators=[DataRequired()],
                             description="Password")
    remember_me = BooleanField("Remember Me",
                               default=True)
    submit = SubmitField("Sign in")


class changePasswordForm(FlaskForm):
    current_password = StringField("Current password",
                                   validators=[DataRequired(), ValidateOldPassword()],
                                   description="Current password")
    new_password = StringField("New password",
                               validators=[DataRequired(), NotEqualTo("current_password")],
                               description="New password")
    submit = SubmitField("Change password")

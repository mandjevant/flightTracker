from flask_wtf import FlaskForm
from flask import flash
from flask_login import current_user
from wtforms import StringField, SubmitField, DateField, PasswordField, BooleanField, FloatField, MultipleFileField
from wtforms.validators import DataRequired, ValidationError
from app.models import User
import datetime


class NotEqualTo(object):
    """
    Form validation class
     for changing password form
     new and old password must not be identical
    """

    def __init__(self, fieldname):
        """
        Initiate class variables
        :param fieldname: form field name
        """
        self.fieldname = fieldname

    def __call__(self, form, field):
        """
        Check if new and old password are identical
         raise validation error if so
        """
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext(f"Invalid field name {self.fieldname}."))

        if field.data == other.data:
            flash("Current password and new password must not be identical.")
            raise ValidationError("Passwords are identical.")


class ValidateOldPassword(object):
    """
    Form validation class
     for changing password form
     validating old password
    """

    def __call__(self, form, field):
        """
        Check if old password field matches the old password
         raise validation error if not
        """
        user = User.query.filter_by(username=current_user.username).first()
        if not user.check_password(field.data):
            flash("Wrong current password.")
            raise ValidationError("Wrong current password.")


class ValidateAdmin(object):
    """
    Form validation class
     user management
     verify if user is admin or not
    """

    def __init__(self, is_admin: bool = True, message: str = "User is already an admin."):
        """
        Initiate class variables
        :param is_admin: check if user is admin or not | bool
        :param message: custom error message | str
        """
        self.is_admin = is_admin
        self.message = message

    def __call__(self, form, field):
        """
        Verify if the user is an admin or not
         raise validation error if equal to self.is_admin
        """
        user = User.query.filter_by(username=field.data).first()
        if user is None:
            return

        if user.is_admin() == self.is_admin:
            flash(self.message)
            raise ValidationError(self.message)


class ValidateUsername(object):
    """
    Form validation class
     user management
     validate username
    """

    def __init__(self, message: str = "User does not exist", new_user: bool = False):
        """
        Initiate class variables
        :param message: custom error message | str
        :param new_user: validation done for a new user | bool
        """
        self.message = message
        self.new_user = new_user

    def __call__(self, form, field):
        """
        Verify username
         raise validation error when applicable
        """
        user = User.query.filter_by(username=field.data).first()
        if (self.new_user and user is not None) or (not self.new_user and user is None):
            flash(self.message)
            raise ValidationError(self.message)


class addFlightForm(FlaskForm):
    """
    FlaskForm for adding a flight
    """
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
    """
    FlaskForm for searching a flight
    """
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
    """
    FlaskForm for editing a flight
    """
    flightFrom = StringField(label="From airport",
                             description="Enter departure airport")
    flightTo = StringField(label="Destination airport",
                           description="Enter arrival airport")
    aircraft = StringField(label="Aircraft",
                           description="Type of aircraft",
                           default="Boeing 737-800")
    submit = SubmitField("Edit flight")


class removeFlightForm(FlaskForm):
    """
    FlaskForm for removing a flight
    """
    callSign = StringField(label="Call sign",
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
    """
    FlaskForm for adding a user
    """
    username = StringField(label="Username",
                           validators=[DataRequired(),
                                       ValidateUsername(message="User already exists. "
                                                                "Please use a different username.",
                                                        new_user=True)],
                           description="New Username",
                           default="Username",
                           render_kw={"onfocus": "this.value=''"})
    is_admin = BooleanField(label="Admin",
                            default=False)
    submit = SubmitField("Add user")


class upgradeUserForm(FlaskForm):
    """
    FlaskForm for upgrading a user
    """
    username = StringField(label="Username",
                           validators=[DataRequired(), ValidateUsername(), ValidateAdmin()],
                           description="Username",
                           default="Username",
                           render_kw={"onfocus": "this.value=''"})
    submit = SubmitField("Upgrade user")


class downgradeUserForm(FlaskForm):
    """
    FlaskForm for downgrading a user
    """
    username = StringField(label="Username",
                           validators=[DataRequired(), ValidateUsername(),
                                       ValidateAdmin(is_admin=False, message="User is not an admin.")],
                           description="Username",
                           default="Username",
                           render_kw={"onfocus": "this.value=''"})
    submit = SubmitField("Downgrade user")


class removeUserForm(FlaskForm):
    """
    FlaskForm for removing a user
    """
    username = StringField(label="Username",
                           validators=[DataRequired(), ValidateUsername()],
                           description="Username",
                           default="Username",
                           render_kw={"onfocus": "this.value=''"})
    submit = SubmitField("Remove user")


class loginForm(FlaskForm):
    """
    FlaskForm for logging in the application
    """
    username = StringField(label="Username",
                           validators=[DataRequired()],
                           description="Username")
    password = PasswordField(label="Password",
                             validators=[DataRequired()],
                             description="Password")
    remember_me = BooleanField(label="Remember Me",
                               default=True)
    submit = SubmitField("Sign in")


class changePasswordForm(FlaskForm):
    """
    FlaskForm for changing the password
    """
    current_password = StringField(label="Current password",
                                   validators=[DataRequired(), ValidateOldPassword()],
                                   description="Current password")
    new_password = StringField(label="New password",
                               validators=[DataRequired(), NotEqualTo("current_password")],
                               description="New password")
    submit = SubmitField("Change password")


class addAirportForm(FlaskForm):
    """
    FlaskForm for adding an airport
    """
    airport_name = StringField(label="Name",
                               validators=[DataRequired()],
                               description="Airport name",
                               default="Airport name",
                               render_kw={"onfocus": "this.value=''"})
    airport_iata = StringField(label="Iata",
                               validators=[DataRequired()],
                               description="Airport iata",
                               default="Airport iata",
                               render_kw={"onfocus": "this.value=''"})
    airport_city = StringField(label="City",
                               description="Airport city",
                               default="Airport city",
                               render_kw={"onfocus": "this.value=''"})
    airport_longitude = FloatField(label="Longitude",
                                   validators=[DataRequired()],
                                   description="Airport longitude",
                                   default="Longitude",
                                   render_kw={"onfocus": "this.value=''"})
    airport_latitude = FloatField(label="Latitude",
                                  validators=[DataRequired()],
                                  description="Airport latitude",
                                  default="Latitude",
                                  render_kw={"onfocus": "this.value=''"})
    submit = SubmitField("Add airport")


class searchAirportForm(FlaskForm):
    """
    FlaskForm for searching an airport
    """
    airport_iata = StringField(label="Iata",
                               validators=[DataRequired()],
                               description="Airport iata",
                               default="Airport iata",
                               render_kw={"onfocus": "this.value=''"})
    submit = SubmitField("Search airport")


class editAirportForm(FlaskForm):
    """
    FlaskForm for editing an airport
    """
    airport_name = StringField(label="Name",
                               validators=[DataRequired()],
                               description="Airport name")
    airport_iata = StringField(label="Iata",
                               validators=[DataRequired()],
                               description="Airport iata")
    airport_city = StringField(label="City",
                               description="Airport city")
    airport_longitude = FloatField(label="Longitude",
                                   validators=[DataRequired()],
                                   description="Airport longitude")
    airport_latitude = FloatField(label="Latitude",
                                  validators=[DataRequired()],
                                  description="Airport latitude")
    submit = SubmitField("Edit airport")


class supplementAirportForm(FlaskForm):
    """
    FlaskForm for supplementing an airport with images
    """
    pictures = MultipleFileField(label="Images",
                                 validators=(["jpg", "png", "jpeg"]),
                                 description="Upload images",
                                 default="Add images...")
    submit = SubmitField("Add images")


class removeAirportForm(FlaskForm):
    """
    FlaskForm for removing an airport
    """
    airport_iata = StringField(label="Iata",
                               validators=[DataRequired()],
                               description="Airport iata",
                               default="Airport iata",
                               render_kw={"onfocus": "this.value=''"})
    submit = SubmitField("Remove airport")

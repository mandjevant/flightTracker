from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, PasswordField, BooleanField
from wtforms.validators import DataRequired, ValidationError
from app.models import User
import datetime


class addFlightForm(FlaskForm):
    callSign = StringField(label="Call sign",
                           validators=[DataRequired()],
                           description="Add a flight",
                           default="Call sign...")
    date = DateField(label="Date of flight",
                     validators=[DataRequired()],
                     description="Enter date of flight",
                     default=datetime.date.today,
                     format="%Y-%m-%d")
    submit = SubmitField("Add flight")


class editFlightForm(FlaskForm):
    callSign = StringField("Call sign",
                           validators=[DataRequired()],
                           description="Edit a flight",
                           default="Call sign...")
    submit = SubmitField("Edit flight")


class removeFlightForm(FlaskForm):
    callSign = StringField("Call sign",
                           validators=[DataRequired()],
                           description="Remove a flight",
                           default="Call sign...")
    date = DateField(label="Date of flight",
                     validators=[DataRequired()],
                     description="Enter date of flight",
                     default=datetime.date.today,
                     format="%Y-%m-%d")
    submit = SubmitField("Remove flight")


class addUserForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired()],
                           description="New Username",
                           default="New user")
    is_admin = BooleanField("Admin",
                            default=False)
    submit = SubmitField("Add user")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')


class removeUserForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired()],
                           description="Remove Username",
                           default="Remove user")
    submit = SubmitField("Remove user")


class loginForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired()],
                           description="Username",
                           default="Username")
    password = PasswordField("Password",
                             validators=[DataRequired()],
                             description="Password",
                             default="Password")
    remember_me = BooleanField("Remember Me",
                               default=True)
    submit = SubmitField("Login")

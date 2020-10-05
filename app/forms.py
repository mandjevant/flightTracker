from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired
import datetime


class addFlightForm(FlaskForm):
    callSign = StringField(label='Call sign',
                           validators=[DataRequired()],
                           description="Add a flight",
                           default="Call sign...")
    date = DateField(label='Date of flight',
                     validators=[DataRequired()],
                     description="Enter date of flight",
                     default=datetime.date.today,
                     format="%Y-%m-%d")
    submit = SubmitField('Add flight')


class editFlightForm(FlaskForm):
    callSign = StringField('Call sign',
                           validators=[DataRequired()],
                           description="Edit a flight",
                           default="Call sign...")
    submit = SubmitField('Edit flight')


class removeFlightForm(FlaskForm):
    callSign = StringField('Call sign',
                           validators=[DataRequired()],
                           description="Remove a flight",
                           default="Call sign...")
    date = DateField(label='Date of flight',
                     validators=[DataRequired()],
                     description="Enter date of flight",
                     default=datetime.date.today,
                     format="%Y-%m-%d")
    submit = SubmitField('Remove flight')

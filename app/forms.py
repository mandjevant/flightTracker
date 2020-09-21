from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class addFlightForm(FlaskForm):
    callSign = StringField(label='Call sign',
                           validators=[DataRequired()],
                           description="Add a flight",
                           default="Call sign...")
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
    submit = SubmitField('Remove flight')

"""Forms for weather app."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField
from wtforms.validators import InputRequired, Email, NumberRange


class RegisterForm(FlaskForm):
    '''Form for registering as a new user.'''

    email = StringField('Email Address', validators=[Email(), InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class LoginForm(FlaskForm):
    '''Form for logging in as an existing user.'''

    email = StringField('Email Address', validators=[Email(), InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class LocationSearchForm(FlaskForm):
    '''Form for searching a location to get weather info.'''

    latitude = FloatField('Latitude', validators=[
                          InputRequired(), NumberRange(min=-90, max=90)])
    longitude = FloatField('Longitude', validators=[
                           InputRequired(), NumberRange(min=-180, max=180)])

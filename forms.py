"""Forms for weather app."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email


class RegisterForm(FlaskForm):
    '''Form for registering as a new user.'''

    email = StringField('Email Address', validators=[Email(), InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    '''Form for logging in as an existing user.'''

    email = StringField('Email Address', validators=[Email(), InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Submit')


class LocationSearchForm(FlaskForm):
    '''Form for searching a location to get weather info.'''

    location = StringField('Location')
    search = SubmitField('Search')

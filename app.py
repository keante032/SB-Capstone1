from flask import Flask, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import and_
import requests
from capstone_secrets import flask_key
from models import db, connect_db, User, Location, Favorite
from forms import RegisterForm, LoginForm, LocationSearchForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///weather'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = flask_key
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

debug = DebugToolbarExtension(app)


@app.route("/")
def root():
    """Homepage."""

    form = LocationSearchForm()

    if form.validate_on_submit():
        latitude = form.data.latitude
        longitude = form.data.longitude

        resp = requests.get(
            f'https://api.weather.gov/points/{latitude},{longitude}')
        props = resp.properties

        searched_loc = Location(office=props.gridId,
                                grid_x=props.gridX, grid_y=props.gridY)
        existing_loc = Location.query.filter(and_(Location.office == searched_loc.office,
                                             Location.grid_x == searched_loc.grid_x, Location.grid_y == searched_loc.grid_y)).first()

        if not existing_loc:
            db.session.add(searched_loc)
            db.session.commit()
        return redirect(f'/locs/{searched_loc.office}-{searched_loc.grid_x}-{searched_loc.grid_y}')

    else:
        return render_template('index.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def create_user():
    '''Form to register new user, and handle adding.'''

    form = RegisterForm()

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != 'csrf_token'}
        new_user = User.register(**data)

        db.session.add(new_user)
        db.session.commit()

        session['current_user'] = new_user.id  # keep logged in

        flash(f'Welcome!')
        return redirect(f'/users/{session["current_user"]}')

    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    '''Form to login existing user, and handle authenticating.'''

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(email, password)

        if user:
            session['current_user'] = user.email  # keep logged in
            return redirect(f'/users/{session["current_user"]}')

        else:
            form.email.errors = ['Email or password is incorrect.']

    return render_template('login.html', form=form)


@app.route('/locs/<str:office>-<int:grid_x>-<int:grid_y>')
def location_page():
    '''Page showing weather info for a particular location.'''

    this_loc = Location.query.filter(and_(
        Location.office == office, Location.grid_x == grid_x, Location.grid_y == grid_y)).first()

    return render_template('location.html', location=this_loc)

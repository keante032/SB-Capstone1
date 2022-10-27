from flask import Flask, redirect, render_template, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests
from capstone_secrets import FLASK_KEY, API_KEY
from models import db, connect_db, User, Location, Favorite
from forms import RegisterForm, LoginForm, LocationSearchForm
from datetime import datetime as dt

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///weather'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = FLASK_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

connect_db(app)

debug = DebugToolbarExtension(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def do_loc_search(loc_form):
    """Perform location search."""

    location = loc_form.location.data

    resp = requests.get(
        f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/today', params={'include': '', 'key': API_KEY})
    data = resp.json()

    searched_loc = Location(
        address=data['resolvedAddress'], lat=data['latitude'], long=data['longitude'])
    existing_loc = Location.query.filter(
        Location.lat == searched_loc.lat, Location.long == searched_loc.long).first()

    if not existing_loc:
        db.session.add(searched_loc)
        db.session.commit()
        new_loc = Location.query.filter(
            Location.lat == searched_loc.lat, Location.long == searched_loc.long).first()
        loc_id = new_loc.id

    else:
        loc_id = existing_loc.id

    return loc_id


@app.route('/', methods=['GET', 'POST'])
def root():
    """Homepage."""

    loc_form = LocationSearchForm()

    if loc_form.validate_on_submit():
        loc_id = do_loc_search(loc_form)

        return redirect(f'/locs/{loc_id}')

    else:
        return render_template('index.html', loc_form=loc_form, at_root=True)


@app.route('/register', methods=['GET', 'POST'])
def create_user():
    '''Form to register new user, and handle adding.'''

    form = RegisterForm()
    loc_form = LocationSearchForm()

    if loc_form.search.data and loc_form.validate():
        loc_id = do_loc_search(loc_form)

        return redirect(f'/locs/{loc_id}')

    if form.submit.data and form.validate():
        email = form.email.data
        password = form.password.data

        try:
            new_user = User.register(email, password)
            db.session.commit()

        except IntegrityError:
            flash("A user with that email already exists.", 'danger')
            return render_template('register.html', form=form)

        do_login(new_user)

        flash(f'Welcome!')
        return redirect('/')

    else:
        return render_template('register.html', form=form, loc_form=loc_form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    '''Form to login existing user, and handle authenticating.'''

    form = LoginForm()
    loc_form = LocationSearchForm()

    if loc_form.search.data and loc_form.validate():
        loc_id = do_loc_search(loc_form)

        return redirect(f'/locs/{loc_id}')

    if form.submit.data and form.validate():
        email = form.email.data
        password = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(email, password)

        if user:
            do_login(user)
            return redirect('/')

        else:
            form.email.errors = ['Email or password is incorrect.']
            return render_template('login.html', form=form)

    else:
        return render_template('login.html', form=form, loc_form=loc_form)


@app.route('/logout')
def logout():
    '''Clear current user from session and go back to root.'''

    do_logout()

    return redirect('/')


@app.route('/locs/<int:loc_id>', methods=['GET', 'POST'])
def location_page(loc_id):
    '''Page showing weather info for a particular location.'''

    this_loc = Location.query.get_or_404(loc_id)

    loc_form = LocationSearchForm()

    if loc_form.validate_on_submit():
        loc_id = do_loc_search(loc_form)

        return redirect(f'/locs/{loc_id}')

    else:
        resp = requests.get(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{this_loc.lat},{this_loc.long}/next5days', params={
                            'include': 'fcst,days,alerts', 'key': API_KEY})
        data = resp.json()

        for day in data['days']:
            date = dt.strptime(day['datetime'], '%Y-%m-%d')
            day['datetime'] = date.strftime('%b %-d, %Y')

        if this_loc.address:
            loc_name = this_loc.address
        else:
            loc_name = f'{this_loc.lat}, {this_loc.long}'

        return render_template('location.html', data=data, loc=this_loc, loc_name=loc_name, loc_form=loc_form)


@app.route('/update-fav-<int:loc_id>')
def update_fav(loc_id):
    '''Add or remove this location from user's favorites.'''

    if not g.user:
        flash('Must be logged in to use Favorites feature.')
        return redirect(f'/locs/{loc_id}')

    this_loc = Location.query.get_or_404(loc_id)

    g.user.favorites.append(this_loc)
    db.session.commit()

    return redirect(f'/locs/{loc_id}')

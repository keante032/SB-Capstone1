"""Models for weather app."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect this database to Flask app (function is called from app.py)."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    favorites = db.relationship(
        'Location', secondary="favorites", backref="users")

    @classmethod
    def register(cls, email, password):
        '''Register user w/hashed password & return user.'''

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode('utf8')

        # return instance of user w/ email and hashed pwd
        new_user = cls(email=email, password=hashed_utf8)
        db.session.add(new_user)
        return new_user

    @classmethod
    def authenticate(cls, email, password):
        '''Validate that user exists & password is correct.

        Return user if valid; else return False.
        '''

        u = User.query.filter_by(email=email).first()

        if u and bcrypt.check_password_hash(u.password, password):
            # return user instance
            return u
        else:
            return False


class Location(db.Model):
    """A location for which weather data has been fetched."""

    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.Text, nullable=True)
    lat = db.Column(db.Float, nullable=False)
    long = db.Column(db.Float, nullable=False)


class Favorite(db.Model):
    """Locations that a user saves as favorites."""

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
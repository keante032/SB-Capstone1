"""User, Location, Favorite model tests."""

# run these tests like:
#
#    python3 -m unittest tests/models_tests.py

from unittest import TestCase
from sqlalchemy import exc
from flask import session, g
from flask_sqlalchemy import SQLAlchemy
from app import app
from models import db, connect_db, User, Location, Favorite


# different database for tests
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///weather-test"
# don't clutter tests with SQL
app.config['SQLALCHEMY_ECHO'] = False
# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True


class UserModelTestCase(TestCase):
    """Test user model."""

    def setUp(self):
        """Create test client, add sample data."""

        with app.app_context():
            db.drop_all()
            db.create_all()

            u1 = User.register("email1@email.com", "password")
            uid1 = 1111
            u1.id = uid1

            u2 = User.register("email2@email.com", "password")
            uid2 = 2222
            u2.id = uid2

            db.session.commit()

            u1 = User.query.get(uid1)
            u2 = User.query.get(uid2)

            self.u1 = u1
            self.uid1 = uid1

            self.u2 = u2
            self.uid2 = uid2

            self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            res = super().tearDown()
            db.session.rollback()
            return res

    def test_user_model(self):
        """Does basic model work?"""

        with app.app_context():
            u = User(
                email="test@test.com",
                password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()

            # User should have no favorites
            self.assertEqual(len(u.favorites), 0)

    ####
    #
    # Signup Tests
    #
    ####
    def test_valid_signup(self):
        with app.app_context():
            u_test = User.register("testtest@test.com", "password")
            uid = 99999
            u_test.id = uid
            db.session.commit()

            u_test = User.query.get(uid)
            self.assertIsNotNone(u_test)
            self.assertEqual(u_test.email, "testtest@test.com")
            self.assertNotEqual(u_test.password, "password")
            # Bcrypt strings should start with $2b$
            self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_email_signup(self):
        with app.app_context():
            invalid = User.register(None, "password")
            uid = 123789
            invalid.id = uid
            with self.assertRaises(exc.IntegrityError) as context:
                db.session.commit()

    def test_invalid_password_signup(self):
        with app.app_context():
            with self.assertRaises(ValueError) as context:
                User.register("email@email.com", "")

            with self.assertRaises(ValueError) as context:
                User.register("email@email.com", None)

    ####
    #
    # Authentication Tests
    #
    ####
    def test_valid_authentication(self):
        with app.app_context():
            u = User.authenticate(self.u1.email, "password")
            self.assertIsNotNone(u)
            self.assertEqual(u.id, self.uid1)

    def test_invalid_email(self):
        with app.app_context():
            self.assertFalse(User.authenticate("bademail@email.com", "password"))

    def test_wrong_password(self):
        with app.app_context():
            self.assertFalse(User.authenticate(self.u1.email, "badpassword"))

class LocationModelTestCase(TestCase):
    """Test location model."""

    def setUp(self):
        """Create test client, add sample data."""

        with app.app_context():
            db.drop_all()
            db.create_all()

            l1 = Location(address="Test1", lat=-90.0, long=-180.0)
            lid1 = 1111
            l1.id = lid1

            l2 = Location(address="Test2", lat=90.0, long=180.0)
            lid2 = 2222
            l2.id = lid2

            db.session.add(l1, l2)
            db.session.commit()

            l1 = Location.query.get(lid1)
            l2 = Location.query.get(lid2)

            self.l1 = l1
            self.lid1 = lid1

            self.l2 = l2
            self.lid2 = lid2

            self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            res = super().tearDown()
            db.session.rollback()
            return res

    def test_location_model(self):
        """Does basic model work?"""

        with app.app_context():
            l = Location(address="Test3", lat=0.0, long=0.0)

            db.session.add(l)
            db.session.commit()

            # Location should have no associated users
            self.assertEqual(len(l.users), 0)

class FavoriteModelTestCase(TestCase):
    """Test favorite model."""

    def setUp(self):
        """Create test client, add sample data."""

        with app.app_context():
            db.drop_all()
            db.create_all()

            u1 = User.register("email1@email.com", "password")
            uid1 = 1111
            u1.id = uid1

            u2 = User.register("email2@email.com", "password")
            uid2 = 2222
            u2.id = uid2

            db.session.commit()

            u1 = User.query.get(uid1)
            u2 = User.query.get(uid2)

            self.u1 = u1
            self.uid1 = uid1

            self.u2 = u2
            self.uid2 = uid2

            l1 = Location(address="Test1", lat=-90.0, long=-180.0)
            lid1 = 1111
            l1.id = lid1

            l2 = Location(address="Test2", lat=90.0, long=180.0)
            lid2 = 2222
            l2.id = lid2

            db.session.add(l1, l2)
            db.session.commit()

            l1 = Location.query.get(lid1)
            l2 = Location.query.get(lid2)

            self.l1 = l1
            self.lid1 = lid1

            self.l2 = l2
            self.lid2 = lid2

            self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            res = super().tearDown()
            db.session.rollback()
            return res

    def test_favorite_model(self):
        """Does basic model work?"""

        with app.app_context():
            f = Favorite(user_id=1111, location_id=1111)

            db.session.add(f)
            db.session.commit()
            
            u1 = User.query.get(1111)
            l1 = Location.query.get(1111)

            # u1 should have 1 favorite
            self.assertEqual(len(u1.favorites), 1)
            
            # l1 should have 1 associated user
            self.assertEqual(len(l1.users), 1)
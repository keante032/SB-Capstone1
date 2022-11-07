"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/views_tests.py

from unittest import TestCase
from sqlalchemy import exc
from flask import session, g
from app import app, CURR_USER_KEY
from models import db, connect_db, User, Location, Favorite

# different database for tests
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///weather-test"
# don't clutter tests with SQL
app.config['SQLALCHEMY_ECHO'] = False
# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True


# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False


class ViewTestCase(TestCase):
    """Test all views."""

    def setUp(self):
        """Create test client, add sample data."""

        with app.app_context():
            db.drop_all()
            db.create_all()

            self.client = app.test_client()

            u1 = User.register("test1@test.com", "password")
            self.uid1 = 778
            u1.id = self.uid1
            u2 = User.register("test2@test.com", "password")
            self.uid2 = 884
            u2.id = self.uid2

            l1 = Location(address="Test1", lat=-90.0, long=-180.0)
            self.lid1 = 1111
            l1.id = self.lid1

            l2 = Location(address="Test2", lat=90.0, long=180.0)
            self.lid2 = 2222
            l2.id = self.lid2

            db.session.add(u1)
            db.session.add(u2)
            db.session.add(l1)
            db.session.add(l2)
            db.session.commit()

            # u1 = User.query.get(self.uid1)
            # u2 = User.query.get(self.uid2)
            # l1 = Location.query.get(self.lid1)
            # l2 = Location.query.get(self.lid2)

    def tearDown(self):
        with app.app_context():
            resp = super().tearDown()
            db.session.rollback()
            return resp

    def test_root(self):
        with self.client as c:
            resp = c.get("/")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Search with a <i>latitude,longitude</i> pair or a city name or an address.", str(resp.data))

    def test_location(self):
        with self.client as c:
            resp = c.get(f"/locs/{self.lid1}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("Test1", str(resp.data))

    def setup_favorites(self):
        with app.app_context():
            u1 = User.query.get(self.uid1)
            l1 = Location.query.get(self.lid1)
            u1.favorites.append(l1)

            u2 = User.query.get(self.uid2)
            l2 = Location.query.get(self.lid2)
            u2.favorites.append(l2)

            db.session.commit()

    def test_root_with_favorites(self):
        self.setup_favorites()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1
            
            resp = c.get("/")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("<h3>Your Favorites</h3>", str(resp.data))
            self.assertIn("Test1", str(resp.data))
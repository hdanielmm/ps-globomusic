import os
import unittest
from config import basedir
from app import create_app, db
from app.models import User


class TestExample(unittest.TestCase):
    def setUp(self):
        # Happens befor each test
        app = create_app("testing")
        self.app_ctx = app.app_context()
        self.app_ctx.push()
        self.app_test_client = app.test_client()
        db.create_all()

    def tearDown(self):
        # Happens after each test
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()

    def test_home_routes(self):
        resp = self.app_test_client.get("/")
        self.assertEqual(resp.status_code, 302)

    def test_user_creation(self):
        u = User(username="test", email="tet@gmail.com")
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()
        u = User.query.filter_by(username="test").first()
        assert u.username == "test"
        assert u.check_password("password123")


if __name__ == "__main__":
    unittest.main()

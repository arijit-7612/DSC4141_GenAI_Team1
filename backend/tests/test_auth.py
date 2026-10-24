import os
import tempfile
import unittest
from pathlib import Path

TEST_DATABASE = Path(tempfile.gettempdir()) / "meal_planner_auth_tests.db"
if TEST_DATABASE.exists(): TEST_DATABASE.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE.as_posix()}"
os.environ["JWT_SECRET"] = "test-secret-with-at-least-thirty-two-bytes"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.database import engine  # noqa: E402


class AuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = TestClient(app)
        cls.client = cls.context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.context.__exit__(None, None, None)
        engine.dispose()
        if TEST_DATABASE.exists(): TEST_DATABASE.unlink()

    def test_register_login_and_me(self):
        register = self.client.post("/auth/register", json={"email": "  Test@Example.com ", "password": "password123"})
        self.assertEqual(register.status_code, 201)
        self.assertNotIn("hashed_password", register.json()["user"])
        self.assertEqual(self.client.post("/auth/register", json={"email": "test@example.com", "password": "password123"}).status_code, 409)
        login = self.client.post("/auth/login", json={"email": "TEST@example.com", "password": "password123"})
        self.assertEqual(login.status_code, 200)
        self.assertEqual(self.client.get("/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"}).status_code, 200)

    def test_invalid_credentials_and_required_fields(self):
        self.assertEqual(self.client.post("/auth/login", json={"email": "none@example.com", "password": "password123"}).status_code, 401)
        self.assertEqual(self.client.post("/auth/login", json={"email": "", "password": ""}).status_code, 422)

import os
import tempfile
import unittest
from pathlib import Path

TEST_DATABASE = Path(tempfile.gettempdir()) / "meal_planner_recipe_tests.db"
if TEST_DATABASE.exists():
    TEST_DATABASE.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE.as_posix()}"

from fastapi.testclient import TestClient  # noqa: E402
from app.database import engine  # noqa: E402
from app.main import app  # noqa: E402


class RecipeApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_context = TestClient(app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)
        engine.dispose()
        if TEST_DATABASE.exists():
            TEST_DATABASE.unlink()

    def test_recipe_crud_with_ingredients(self):
        created = self.client.post(
            "/api/recipes",
            json={
                "name": "Tomato Pasta",
                "ingredients": [
                    {"name": "Pasta", "quantity": 200, "unit": "g"},
                    {"name": "Tomato", "quantity": 3, "unit": "pcs"},
                ],
            },
        )
        self.assertEqual(created.status_code, 201)
        recipe = created.json()
        self.assertEqual(recipe["name"], "Tomato Pasta")
        self.assertEqual(recipe["ingredients"], [
            {"id": recipe["ingredients"][0]["id"], "name": "Pasta", "quantity": 200.0, "unit": "g"},
            {"id": recipe["ingredients"][1]["id"], "name": "Tomato", "quantity": 3.0, "unit": "pcs"},
        ])

        listed = self.client.get("/api/recipes")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual([item["id"] for item in listed.json()], [recipe["id"]])

        viewed = self.client.get(f"/api/recipes/{recipe['id']}")
        self.assertEqual(viewed.status_code, 200)
        self.assertEqual(viewed.json()["ingredients"][1]["name"], "Tomato")

        updated = self.client.put(
            f"/api/recipes/{recipe['id']}",
            json={
                "name": "Tomato Basil Pasta",
                "ingredients": [
                    {"name": "Pasta", "quantity": 250, "unit": "g"},
                    {"name": "Basil", "quantity": 10, "unit": "leaves"},
                ],
            },
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["name"], "Tomato Basil Pasta")
        self.assertEqual(
            [(item["name"], item["quantity"]) for item in updated.json()["ingredients"]],
            [("Pasta", 250.0), ("Basil", 10.0)],
        )

        deleted = self.client.delete(f"/api/recipes/{recipe['id']}")
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(self.client.get(f"/api/recipes/{recipe['id']}").status_code, 404)

    def test_recipe_requires_valid_name_and_ingredients(self):
        response = self.client.post(
            "/api/recipes",
            json={
                "name": "   ",
                "ingredients": [
                    {"name": "Pasta", "quantity": 0, "unit": "g"},
                    {"name": "pasta", "quantity": 1, "unit": "g"},
                ],
            },
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()

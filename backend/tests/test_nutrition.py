import os
import tempfile
import unittest
from pathlib import Path

TEST_DATABASE = Path(tempfile.gettempdir()) / "meal_planner_nutrition_tests.db"
if TEST_DATABASE.exists():
    TEST_DATABASE.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE.as_posix()}"
os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient  # noqa: E402
from app.database import engine  # noqa: E402
from app.main import app  # noqa: E402


class NutritionApiTests(unittest.TestCase):
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

    def setUp(self):
        self.created_recipe_ids: list[int] = []

    def tearDown(self):
        for rid in self.created_recipe_ids:
            self.client.delete(f"/api/recipes/{rid}")

    def test_nutrition_calculation_and_serving_scaling(self):
        # Create a recipe with known ingredients:
        # Chicken Breast 200g, Olive Oil 14g (1 tbsp), White Rice 100g
        created = self.client.post(
            "/api/recipes",
            json={
                "name": "Chicken and Rice",
                "ingredients": [
                    {"name": "Chicken Breast", "quantity": 200, "unit": "g"},
                    {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
                    {"name": "White Rice", "quantity": 100, "unit": "g"},
                ],
            },
        )
        self.assertEqual(created.status_code, 201)
        recipe = created.json()
        recipe_id = recipe["id"]
        self.created_recipe_ids.append(recipe_id)

        # Check nutrition in recipe serialization
        self.assertIn("nutrition", recipe)
        nutrition = recipe["nutrition"]
        self.assertIsNotNone(nutrition)
        self.assertIn("per_serving", nutrition)
        self.assertIn("total", nutrition)
        self.assertIn("dietary_tags", nutrition)
        self.assertIn("allergens", nutrition)

        # High-protein should be detected because chicken breast 200g has ~62g protein (> 25g)
        self.assertIn("High-Protein", nutrition["dietary_tags"])
        # Dairy-Free and Gluten-Free should be present
        self.assertIn("Dairy-Free", nutrition["dietary_tags"])
        self.assertIn("Gluten-Free", nutrition["dietary_tags"])
        # Not vegan or vegetarian
        self.assertNotIn("Vegan", nutrition["dietary_tags"])
        self.assertNotIn("Vegetarian", nutrition["dietary_tags"])

        # Fetch nutrition endpoint with 1 serving
        res_1 = self.client.get(f"/api/recipes/{recipe_id}/nutrition?servings=1")
        self.assertEqual(res_1.status_code, 200)
        nut_1 = res_1.json()
        self.assertEqual(nut_1["servings"], 1)
        self.assertEqual(nut_1["confidence_score"], 1.0)
        self.assertFalse(nut_1["is_estimate"])
        self.assertEqual(nut_1["unmatched_ingredients"], [])

        per_serving_cal = nut_1["per_serving"]["calories"]
        self.assertGreater(per_serving_cal, 400)
        self.assertGreater(nut_1["per_serving"]["protein"], 60.0)

        # Fetch nutrition endpoint with 3 servings
        res_3 = self.client.get(f"/api/recipes/{recipe_id}/nutrition?servings=3")
        self.assertEqual(res_3.status_code, 200)
        nut_3 = res_3.json()
        self.assertEqual(nut_3["servings"], 3)
        # Per serving stays identical
        self.assertEqual(nut_3["per_serving"]["calories"], per_serving_cal)
        # Total scales by 3
        self.assertEqual(nut_3["total"]["calories"], per_serving_cal * 3)
        self.assertAlmostEqual(
            nut_3["total"]["protein"], nut_1["per_serving"]["protein"] * 3, places=1
        )

    def test_allergen_and_dietary_detection(self):
        # Create a recipe with Peanut Butter and Oats and Milk
        created = self.client.post(
            "/api/recipes",
            json={
                "name": "Peanut Butter Oatmeal",
                "ingredients": [
                    {"name": "Rolled Oats", "quantity": 50, "unit": "g"},
                    {"name": "Milk", "quantity": 200, "unit": "ml"},
                    {"name": "Peanut Butter", "quantity": 2, "unit": "tbsp"},
                ],
            },
        )
        self.assertEqual(created.status_code, 201)
        recipe_id = created.json()["id"]
        self.created_recipe_ids.append(recipe_id)

        res = self.client.get(f"/api/recipes/{recipe_id}/nutrition")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Should identify allergens: Milk, Peanuts, Wheat / Gluten (from oats)
        self.assertIn("Milk", data["allergens"])
        self.assertIn("Peanuts", data["allergens"])
        self.assertIn("Vegetarian", data["dietary_tags"])
        self.assertNotIn("Vegan", data["dietary_tags"])
        self.assertNotIn("Dairy-Free", data["dietary_tags"])

    def test_unmatched_ingredient_handling(self):
        created = self.client.post(
            "/api/recipes",
            json={
                "name": "Mysterious Stew",
                "ingredients": [
                    {"name": "Potato", "quantity": 100, "unit": "g"},
                    {"name": "Exotic Martian Herb", "quantity": 10, "unit": "g"},
                ],
            },
        )
        self.assertEqual(created.status_code, 201)
        recipe_id = created.json()["id"]
        self.created_recipe_ids.append(recipe_id)

        res = self.client.get(f"/api/recipes/{recipe_id}/nutrition")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertTrue(data["is_estimate"])
        self.assertIn("Exotic Martian Herb", data["unmatched_ingredients"])
        self.assertNotIn("Potato", data["unmatched_ingredients"])
        self.assertEqual(data["confidence_score"], 0.5)

    def test_user_profile_crud(self):
        # Get default profile
        res = self.client.get("/api/profile")
        self.assertEqual(res.status_code, 200)
        profile = res.json()
        self.assertEqual(profile["username"], "default_user")

        # Update profile
        update_res = self.client.put(
            "/api/profile",
            json={
                "dietary_preferences": ["Vegetarian", "High-Protein"],
                "allergies": ["Peanuts", "Shellfish"],
            },
        )
        self.assertEqual(update_res.status_code, 200)
        updated = update_res.json()
        self.assertEqual(updated["dietary_preferences"], ["Vegetarian", "High-Protein"])
        self.assertEqual(updated["allergies"], ["Peanuts", "Shellfish"])

        # Fetch again to verify persistence
        get_res = self.client.get("/api/profile")
        self.assertEqual(get_res.status_code, 200)
        persisted = get_res.json()
        self.assertEqual(persisted["dietary_preferences"], ["Vegetarian", "High-Protein"])
        self.assertEqual(persisted["allergies"], ["Peanuts", "Shellfish"])

    def test_nutrition_invalid_servings(self):
        res = self.client.get("/api/recipes/1/nutrition?servings=0")
        self.assertEqual(res.status_code, 422)

    def test_usda_api_integration_for_new_ingredient(self):
        # Create a recipe with Strawberry (which is resolved live via USDA FoodData Central)
        created = self.client.post(
            "/api/recipes",
            json={
                "name": "Strawberry Snack",
                "ingredients": [
                    {"name": "Strawberry", "quantity": 100, "unit": "g"},
                ],
            },
        )
        self.assertEqual(created.status_code, 201)
        recipe = created.json()
        recipe_id = recipe["id"]
        self.created_recipe_ids.append(recipe_id)

        nutrition = recipe.get("nutrition")
        self.assertIsNotNone(nutrition)
        self.assertEqual(nutrition["confidence_score"], 1.0)
        self.assertFalse(nutrition["is_estimate"])
        # Strawberries have around 32 kcal and ~7.7g carbs
        self.assertGreater(nutrition["per_serving"]["calories"], 20)
        self.assertGreater(nutrition["per_serving"]["carbohydrates"], 5.0)


if __name__ == "__main__":
    unittest.main()

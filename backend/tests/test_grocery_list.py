import os
import tempfile
import unittest
from pathlib import Path

TEST_DATABASE = Path(tempfile.gettempdir()) / "meal_planner_grocery_tests.db"
if TEST_DATABASE.exists():
    TEST_DATABASE.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE.as_posix()}"
os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient  # noqa: E402
from app.database import engine  # noqa: E402
from app.main import app  # noqa: E402


class GroceryListAndMealPlanTests(unittest.TestCase):
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
        # Clear meal plan before each test
        self.client.delete("/api/meal-plan")

    def test_empty_meal_plan_generates_empty_grocery_list(self):
        response = self.client.get("/api/grocery-list")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["items"], [])
        self.assertEqual(data["total_items"], 0)
        self.assertEqual(data["planned_meals_count"], 0)

    def test_acceptance_criteria_1_and_3_single_recipe_in_plan(self):
        """
        Criterion 1: Grocery list includes ingredients from recipes in the meal plan.
        Criterion 3: Ingredient quantities are shown when available.
        """
        # Create a recipe: Tomato Pasta
        recipe_res = self.client.post(
            "/api/recipes",
            json={
                "name": "Quick Tomato Pasta",
                "ingredients": [
                    {"name": "Pasta", "quantity": 200, "unit": "g"},
                    {"name": "Tomato", "quantity": 3, "unit": "piece"},
                    {"name": "Olive Oil", "quantity": 2, "unit": "tbsp"},
                ],
            },
        )
        self.assertEqual(recipe_res.status_code, 201)
        recipe_id = recipe_res.json()["id"]

        # Add recipe to meal plan on Monday Lunch
        plan_res = self.client.post(
            "/api/meal-plan",
            json={"day": "Monday", "meal": "Lunch", "recipe_id": recipe_id},
        )
        self.assertEqual(plan_res.status_code, 200)

        # Fetch grocery list
        grocery_res = self.client.get("/api/grocery-list")
        self.assertEqual(grocery_res.status_code, 200)
        data = grocery_res.json()
        self.assertEqual(data["total_recipes"], 1)
        self.assertEqual(data["planned_meals_count"], 1)
        self.assertEqual(data["total_items"], 3)

        items_by_name = {item["name"]: item for item in data["items"]}
        self.assertIn("Pasta", items_by_name)
        self.assertEqual(items_by_name["Pasta"]["quantity"], 200.0)
        self.assertEqual(items_by_name["Pasta"]["unit"], "g")

        self.assertIn("Tomato", items_by_name)
        self.assertEqual(items_by_name["Tomato"]["quantity"], 3.0)
        self.assertEqual(items_by_name["Tomato"]["unit"], "piece")

        self.assertIn("Olive Oil", items_by_name)
        self.assertEqual(items_by_name["Olive Oil"]["quantity"], 2.0)
        self.assertEqual(items_by_name["Olive Oil"]["unit"], "tbsp")

    def test_acceptance_criteria_2_and_3_multiple_recipes_aggregated(self):
        """
        Criterion 2: Ingredients from multiple planned recipes are included.
        Criterion 3: Ingredient quantities are aggregated and shown.
        """
        # Create Recipe 1: Salad
        r1 = self.client.post(
            "/api/recipes",
            json={
                "name": "Greek Salad",
                "ingredients": [
                    {"name": "Tomato", "quantity": 2, "unit": "piece"},
                    {"name": "Cucumber", "quantity": 1, "unit": "piece"},
                    {"name": "Feta", "quantity": 100, "unit": "g"},
                ],
            },
        ).json()

        # Create Recipe 2: Bruschetta
        r2 = self.client.post(
            "/api/recipes",
            json={
                "name": "Tomato Bruschetta",
                "ingredients": [
                    {"name": "Tomato", "quantity": 4, "unit": "piece"},
                    {"name": "Bread", "quantity": 4, "unit": "slice"},
                    {"name": "Garlic", "quantity": 2, "unit": "clove"},
                ],
            },
        ).json()

        # Assign both to the meal plan
        self.client.post(
            "/api/meal-plan",
            json={"day": "Tuesday", "meal": "Lunch", "recipe_id": r1["id"]},
        )
        self.client.post(
            "/api/meal-plan",
            json={"day": "Wednesday", "meal": "Dinner", "recipe_id": r2["id"]},
        )

        grocery_res = self.client.get("/api/grocery-list")
        self.assertEqual(grocery_res.status_code, 200)
        data = grocery_res.json()

        self.assertEqual(data["total_recipes"], 2)
        self.assertEqual(data["planned_meals_count"], 2)

        items_by_name = {item["name"]: item for item in data["items"]}

        # Tomato should be aggregated: 2 (from Salad) + 4 (from Bruschetta) = 6
        self.assertIn("Tomato", items_by_name)
        self.assertEqual(items_by_name["Tomato"]["quantity"], 6.0)
        self.assertEqual(items_by_name["Tomato"]["unit"], "piece")
        self.assertCountEqual(
            items_by_name["Tomato"]["recipes"], ["Greek Salad", "Tomato Bruschetta"]
        )

        # Other distinct ingredients should be present
        self.assertIn("Cucumber", items_by_name)
        self.assertIn("Feta", items_by_name)
        self.assertIn("Bread", items_by_name)
        self.assertIn("Garlic", items_by_name)

    def test_acceptance_criterion_4_grocery_list_updates_when_meal_plan_changes(self):
        """
        Criterion 4: The grocery list updates when the weekly meal plan changes.
        """
        # Create 2 different recipes
        soup = self.client.post(
            "/api/recipes",
            json={
                "name": "Chicken Soup",
                "ingredients": [
                    {"name": "Chicken", "quantity": 500, "unit": "g"},
                    {"name": "Carrot", "quantity": 2, "unit": "piece"},
                ],
            },
        ).json()

        stirfry = self.client.post(
            "/api/recipes",
            json={
                "name": "Tofu Stirfry",
                "ingredients": [
                    {"name": "Tofu", "quantity": 250, "unit": "g"},
                    {"name": "Broccoli", "quantity": 1, "unit": "bunch"},
                ],
            },
        ).json()

        # Step 1: Assign Chicken Soup to Friday Dinner
        self.client.post(
            "/api/meal-plan",
            json={"day": "Friday", "meal": "Dinner", "recipe_id": soup["id"]},
        )

        g1 = self.client.get("/api/grocery-list").json()
        item_names_1 = [i["name"] for i in g1["items"]]
        self.assertIn("Chicken", item_names_1)
        self.assertNotIn("Tofu", item_names_1)

        # Step 2: Change Friday Dinner to Tofu Stirfry (overwrite slot)
        self.client.post(
            "/api/meal-plan",
            json={"day": "Friday", "meal": "Dinner", "recipe_id": stirfry["id"]},
        )

        g2 = self.client.get("/api/grocery-list").json()
        item_names_2 = [i["name"] for i in g2["items"]]
        # Now Tofu should be present, Chicken should NOT be present
        self.assertIn("Tofu", item_names_2)
        self.assertIn("Broccoli", item_names_2)
        self.assertNotIn("Chicken", item_names_2)

        # Step 3: Remove Friday Dinner entirely
        self.client.delete("/api/meal-plan/Friday/Dinner")

        g3 = self.client.get("/api/grocery-list").json()
        self.assertEqual(g3["items"], [])
        self.assertEqual(g3["total_items"], 0)

    def test_grocery_list_categorization_and_hidden_quantities_for_seasonings(self):
        """
        Verify that:
        1. Substantive ingredients (Chicken, Eggs) show exact quantities.
        2. Spices and pantry staples (Salt, Garlic, Olive Oil) have show_quantity=False.
        3. Response includes categorized groupings (categories).
        """
        recipe = self.client.post(
            "/api/recipes",
            json={
                "name": "Garlic Roast Chicken",
                "ingredients": [
                    {"name": "Chicken Breast", "quantity": 160, "unit": "g"},
                    {"name": "Garlic", "quantity": 3, "unit": "clove"},
                    {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
                    {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
                ],
            },
        ).json()

        self.client.post(
            "/api/meal-plan",
            json={"day": "Saturday", "meal": "Dinner", "recipe_id": recipe["id"]},
        )

        res = self.client.get("/api/grocery-list")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        items_by_name = {item["name"]: item for item in data["items"]}

        # Chicken: Meat & Seafood, show_quantity is True
        self.assertTrue(items_by_name["Chicken Breast"]["show_quantity"])
        self.assertEqual(items_by_name["Chicken Breast"]["category"], "Meat & Seafood")
        self.assertEqual(items_by_name["Chicken Breast"]["display_quantity"], "160 g")

        # Salt: Spices & Seasonings, show_quantity is False
        self.assertFalse(items_by_name["Salt"]["show_quantity"])
        self.assertEqual(items_by_name["Salt"]["category"], "Spices & Seasonings")
        self.assertEqual(items_by_name["Salt"]["display_quantity"], "Pantry staple")

        # Garlic: Spices & Seasonings, show_quantity is False
        self.assertFalse(items_by_name["Garlic"]["show_quantity"])
        self.assertEqual(items_by_name["Garlic"]["category"], "Spices & Seasonings")

        # Categories grouping
        categories_dict = {cat["category"]: cat["items"] for cat in data["categories"]}
        self.assertIn("Meat & Seafood", categories_dict)
        self.assertIn("Spices & Seasonings", categories_dict)
        meat_item_names = [i["name"] for i in categories_dict["Meat & Seafood"]]
        self.assertIn("Chicken Breast", meat_item_names)

    def test_deduplication_and_portion_suppression(self):
        """
        Verify that:
        1. Bread, Butter, Cheese do NOT show slice / tbsp / portion quantities.
        2. Ingredients used across multiple recipes (like Olive Oil with tbsp vs tsp)
           are NEVER duplicated on the grocery list.
        3. Exact measurement items (Chicken Breast, Eggs) combine quantities.
        """
        r1 = self.client.post(
            "/api/recipes",
            json={
                "name": "Avocado Toast With Egg",
                "ingredients": [
                    {"name": "Sourdough Bread", "quantity": 1, "unit": "slice"},
                    {"name": "Olive Oil", "quantity": 1, "unit": "tsp"},
                    {"name": "Egg", "quantity": 2, "unit": "piece"},
                ],
            },
        ).json()

        r2 = self.client.post(
            "/api/recipes",
            json={
                "name": "Banana Pancakes",
                "ingredients": [
                    {"name": "Butter", "quantity": 1, "unit": "tbsp"},
                    {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
                    {"name": "Egg", "quantity": 2, "unit": "piece"},
                ],
            },
        ).json()

        # Add both to meal plan
        self.client.post("/api/meal-plan", json={"day": "Monday", "meal": "Breakfast", "recipe_id": r1["id"]})
        self.client.post("/api/meal-plan", json={"day": "Tuesday", "meal": "Breakfast", "recipe_id": r2["id"]})

        res = self.client.get("/api/grocery-list")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Check all item names - NO DUPLICATES ALLOWED
        all_names = [item["name"] for item in data["items"]]
        self.assertEqual(len(all_names), len(set(all_names)), f"Duplicates found in grocery list: {all_names}")

        items_by_name = {item["name"]: item for item in data["items"]}

        # Sourdough Bread: show_quantity must be False (no "1 slice bread")
        self.assertIn("Sourdough Bread", items_by_name)
        self.assertFalse(items_by_name["Sourdough Bread"]["show_quantity"])

        # Butter: show_quantity must be False (no "1 tbsp butter")
        self.assertIn("Butter", items_by_name)
        self.assertFalse(items_by_name["Butter"]["show_quantity"])

        # Olive Oil: used in both recipes (1 tsp vs 1 tbsp) -> MUST BE SINGLE ENTRY
        self.assertIn("Olive Oil", items_by_name)
        self.assertFalse(items_by_name["Olive Oil"]["show_quantity"])
        self.assertCountEqual(
            items_by_name["Olive Oil"]["recipes"],
            ["Avocado Toast With Egg", "Banana Pancakes"],
        )

        # Egg: exact measurement (2 piece + 2 piece) -> COMBINED to 4 piece
        self.assertIn("Egg", items_by_name)
        self.assertTrue(items_by_name["Egg"]["show_quantity"])
        self.assertEqual(items_by_name["Egg"]["quantity"], 4.0)
        self.assertEqual(items_by_name["Egg"]["unit"], "piece")
        self.assertEqual(items_by_name["Egg"]["display_quantity"], "4 piece")


if __name__ == "__main__":
    unittest.main()

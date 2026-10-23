"""Preloaded single-serving recipes with comprehensive ingredient lists including spices, seasonings, and oils."""

import os

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Recipe
from app.schemas.recipe import RecipeCreate, RecipeIngredientInput
from app.services.recipe_service import create_recipe

PRELOADED_RECIPES: list[dict] = [
    {
        "name": "Classic Oatmeal with Berries",
        "ingredients": [
            {"name": "Rolled Oats", "quantity": 45, "unit": "g"},
            {"name": "Milk", "quantity": 180, "unit": "ml"},
            {"name": "Mixed Berries", "quantity": 60, "unit": "g"},
            {"name": "Honey", "quantity": 1, "unit": "tbsp"},
            {"name": "Brown Sugar", "quantity": 1, "unit": "tsp"},
            {"name": "Cinnamon Powder", "quantity": 0.5, "unit": "tsp"},
            {"name": "Chia Seeds", "quantity": 1, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    {
        "name": "Avocado Toast with Egg",
        "ingredients": [
            {"name": "Sourdough Bread", "quantity": 1, "unit": "slice"},
            {"name": "Avocado", "quantity": 1, "unit": "piece"},
            {"name": "Egg", "quantity": 1, "unit": "piece"},
            {"name": "Lemon", "quantity": 1, "unit": "piece"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
            {"name": "Red Chili Flakes", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    {
        "name": "Greek Yogurt Parfait",
        "ingredients": [
            {"name": "Greek Yogurt", "quantity": 150, "unit": "g"},
            {"name": "Granola", "quantity": 35, "unit": "g"},
            {"name": "Honey", "quantity": 1, "unit": "tbsp"},
            {"name": "Banana", "quantity": 1, "unit": "piece"},
            {"name": "Chia Seeds", "quantity": 1, "unit": "tsp"},
            {"name": "Cinnamon Powder", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    {
        "name": "Fluffy Banana Pancakes",
        "ingredients": [
            {"name": "All-Purpose Flour", "quantity": 70, "unit": "g"},
            {"name": "Banana", "quantity": 1, "unit": "piece"},
            {"name": "Egg", "quantity": 1, "unit": "piece"},
            {"name": "Milk", "quantity": 80, "unit": "ml"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp"},
            {"name": "White Sugar", "quantity": 1, "unit": "tbsp"},
            {"name": "Baking Powder", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
            {"name": "Vanilla Extract", "quantity": 0.5, "unit": "tsp"},
        ],
    },
    {
        "name": "Spinach & Mushroom Omelette",
        "ingredients": [
            {"name": "Egg", "quantity": 2, "unit": "piece"},
            {"name": "Fresh Spinach", "quantity": 50, "unit": "g"},
            {"name": "Mushroom", "quantity": 50, "unit": "g"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp"},
            {"name": "Cheddar Cheese", "quantity": 25, "unit": "g"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    {
        "name": "Mediterranean Chickpea Salad",
        "ingredients": [
            {"name": "Chickpeas", "quantity": 120, "unit": "g"},
            {"name": "Cucumber", "quantity": 1, "unit": "piece"},
            {"name": "Tomato", "quantity": 1, "unit": "piece"},
            {"name": "Red Onion", "quantity": 1, "unit": "piece"},
            {"name": "Feta Cheese", "quantity": 40, "unit": "g"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Lemon", "quantity": 1, "unit": "piece"},
            {"name": "Dried Oregano", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    {
        "name": "Grilled Chicken Caesar Salad",
        "ingredients": [
            {"name": "Chicken Breast", "quantity": 160, "unit": "g"},
            {"name": "Romaine Lettuce", "quantity": 1, "unit": "bunch"},
            {"name": "Parmesan Cheese", "quantity": 25, "unit": "g"},
            {"name": "Croutons", "quantity": 30, "unit": "g"},
            {"name": "Caesar Dressing", "quantity": 2, "unit": "tbsp"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Garlic", "quantity": 1, "unit": "clove"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    {
        "name": "Quinoa & Roasted Veggie Bowl",
        "ingredients": [
            {"name": "Quinoa", "quantity": 70, "unit": "g"},
            {"name": "Bell Pepper", "quantity": 1, "unit": "piece"},
            {"name": "Zucchini", "quantity": 1, "unit": "piece"},
            {"name": "Red Onion", "quantity": 1, "unit": "piece"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Smoked Paprika", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    {
        "name": "Paneer Tikka Wrap",
        "ingredients": [
            {"name": "Paneer", "quantity": 110, "unit": "g"},
            {"name": "Tortilla Wrap", "quantity": 1, "unit": "piece"},
            {"name": "Onion", "quantity": 1, "unit": "piece"},
            {"name": "Bell Pepper", "quantity": 1, "unit": "piece"},
            {"name": "Greek Yogurt", "quantity": 2, "unit": "tbsp"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Ginger Garlic Paste", "quantity": 1, "unit": "tsp"},
            {"name": "Garam Masala", "quantity": 0.5, "unit": "tsp"},
            {"name": "Red Chili Powder", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
        ],
    },
    {
        "name": "Creamy Tomato Basil Pasta",
        "ingredients": [
            {"name": "Penne Pasta", "quantity": 85, "unit": "g"},
            {"name": "Tomato", "quantity": 2, "unit": "piece"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Fresh Basil", "quantity": 1, "unit": "bunch"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Heavy Cream", "quantity": 30, "unit": "ml"},
            {"name": "Parmesan Cheese", "quantity": 25, "unit": "g"},
            {"name": "White Sugar", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    {
        "name": "Chicken Stir Fry with Vegetables",
        "ingredients": [
            {"name": "Chicken Breast", "quantity": 160, "unit": "g"},
            {"name": "Broccoli", "quantity": 1, "unit": "bunch"},
            {"name": "Carrot", "quantity": 1, "unit": "piece"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Soy Sauce", "quantity": 1, "unit": "tbsp"},
            {"name": "Sesame Oil", "quantity": 1, "unit": "tsp"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Brown Sugar", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    {
        "name": "Vegetable Lentil Curry",
        "ingredients": [
            {"name": "Red Lentils", "quantity": 75, "unit": "g"},
            {"name": "Onion", "quantity": 1, "unit": "piece"},
            {"name": "Tomato", "quantity": 1, "unit": "piece"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Turmeric Powder", "quantity": 0.5, "unit": "tsp"},
            {"name": "Cumin Seeds", "quantity": 0.5, "unit": "tsp"},
            {"name": "Garam Masala", "quantity": 0.5, "unit": "tsp"},
            {"name": "Red Chili Powder", "quantity": 0.25, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
        ],
    },
    {
        "name": "Pan-Seared Salmon with Asparagus",
        "ingredients": [
            {"name": "Salmon Fillet", "quantity": 160, "unit": "g"},
            {"name": "Asparagus", "quantity": 1, "unit": "bunch"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tsp"},
            {"name": "Lemon", "quantity": 1, "unit": "piece"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    {
        "name": "Tofu & Mushroom Fried Rice",
        "ingredients": [
            {"name": "Basmati Rice", "quantity": 75, "unit": "g"},
            {"name": "Firm Tofu", "quantity": 100, "unit": "g"},
            {"name": "Mushroom", "quantity": 70, "unit": "g"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Green Onion", "quantity": 1, "unit": "bunch"},
            {"name": "Soy Sauce", "quantity": 1, "unit": "tbsp"},
            {"name": "Sesame Oil", "quantity": 1, "unit": "tsp"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
]


def seed_recipes_if_empty(db: Session) -> int:
    """Preload standard recipes if database has no recipes."""
    if os.getenv("TESTING") == "1":
        return 0

    count = db.scalar(select(func.count(Recipe.id)))
    if count and count > 0:
        return 0

    added = 0
    for item in PRELOADED_RECIPES:
        payload = RecipeCreate(
            name=item["name"],
            ingredients=[RecipeIngredientInput(**i) for i in item["ingredients"]],
        )
        create_recipe(db, payload)
        added += 1

    return added


def reload_preloaded_recipes(db: Session) -> int:
    """Remove existing recipes and reload with curated preloaded recipes."""
    recipes = db.scalars(select(Recipe)).all()
    for recipe in recipes:
        db.delete(recipe)
    db.commit()

    return seed_recipes_if_empty(db)

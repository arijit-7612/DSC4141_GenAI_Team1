"""Preloaded single-serving recipes with comprehensive ingredient lists including spices, seasonings, and oils."""

import os

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Recipe
from app.schemas.recipe import RecipeCreate, RecipeIngredientInput
from app.services.recipe_service import create_recipe

PRELOADED_RECIPES: list[dict] = [
    # --- Original 14 Curated Recipes ---
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

    # --- 30 Additional Curated Recipes (Breakfast, Lunch, Dinner | Veg & Non-Veg) ---

    # 1. Breakfast - Veg
    {
        "name": "Blueberry Chia Seed Pudding",
        "ingredients": [
            {"name": "Almond Milk", "quantity": 180, "unit": "ml"},
            {"name": "Chia Seeds", "quantity": 25, "unit": "g"},
            {"name": "Blueberries", "quantity": 60, "unit": "g"},
            {"name": "Honey", "quantity": 1, "unit": "tbsp"},
            {"name": "Vanilla Extract", "quantity": 0.5, "unit": "tsp"},
        ],
    },
    # 2. Breakfast - Veg
    {
        "name": "Peanut Butter Banana Toast",
        "ingredients": [
            {"name": "Sourdough Bread", "quantity": 1, "unit": "slice"},
            {"name": "Peanut Butter", "quantity": 2, "unit": "tbsp"},
            {"name": "Banana", "quantity": 1, "unit": "piece"},
            {"name": "Chia Seeds", "quantity": 1, "unit": "tsp"},
            {"name": "Cinnamon Powder", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 3. Breakfast - Veg
    {
        "name": "Masala Tofu Scramble",
        "ingredients": [
            {"name": "Firm Tofu", "quantity": 150, "unit": "g"},
            {"name": "Onion", "quantity": 1, "unit": "piece"},
            {"name": "Tomato", "quantity": 1, "unit": "piece"},
            {"name": "Fresh Spinach", "quantity": 40, "unit": "g"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Turmeric Powder", "quantity": 0.5, "unit": "tsp"},
            {"name": "Cumin Seeds", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 4. Breakfast - Veg
    {
        "name": "Apple Cinnamon Overnight Oats",
        "ingredients": [
            {"name": "Rolled Oats", "quantity": 50, "unit": "g"},
            {"name": "Almond Milk", "quantity": 160, "unit": "ml"},
            {"name": "Apple", "quantity": 1, "unit": "piece"},
            {"name": "Honey", "quantity": 1, "unit": "tbsp"},
            {"name": "Chia Seeds", "quantity": 1, "unit": "tsp"},
            {"name": "Cinnamon Powder", "quantity": 0.5, "unit": "tsp"},
        ],
    },
    # 5. Breakfast - Veg
    {
        "name": "Whole Wheat Berry Waffles",
        "ingredients": [
            {"name": "All-Purpose Flour", "quantity": 70, "unit": "g"},
            {"name": "Milk", "quantity": 90, "unit": "ml"},
            {"name": "Egg", "quantity": 1, "unit": "piece"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp"},
            {"name": "Mixed Berries", "quantity": 50, "unit": "g"},
            {"name": "Maple Syrup", "quantity": 1, "unit": "tbsp"},
            {"name": "Baking Powder", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 6. Breakfast - Non-Veg
    {
        "name": "Scrambled Eggs with Smoked Salmon",
        "ingredients": [
            {"name": "Egg", "quantity": 2, "unit": "piece"},
            {"name": "Smoked Salmon", "quantity": 60, "unit": "g"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp"},
            {"name": "Fresh Spinach", "quantity": 30, "unit": "g"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 7. Breakfast - Non-Veg
    {
        "name": "Breakfast Burrito with Bacon & Egg",
        "ingredients": [
            {"name": "Tortilla Wrap", "quantity": 1, "unit": "piece"},
            {"name": "Egg", "quantity": 2, "unit": "piece"},
            {"name": "Bacon", "quantity": 40, "unit": "g"},
            {"name": "Cheddar Cheese", "quantity": 25, "unit": "g"},
            {"name": "Bell Pepper", "quantity": 1, "unit": "piece"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 8. Breakfast - Non-Veg
    {
        "name": "Turkey Bacon & Egg Wrap",
        "ingredients": [
            {"name": "Tortilla Wrap", "quantity": 1, "unit": "piece"},
            {"name": "Egg", "quantity": 2, "unit": "piece"},
            {"name": "Turkey Bacon", "quantity": 35, "unit": "g"},
            {"name": "Fresh Spinach", "quantity": 40, "unit": "g"},
            {"name": "Cheddar Cheese", "quantity": 20, "unit": "g"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 9. Breakfast - Non-Veg
    {
        "name": "Shakshuka with Poached Eggs",
        "ingredients": [
            {"name": "Egg", "quantity": 2, "unit": "piece"},
            {"name": "Tomato", "quantity": 2, "unit": "piece"},
            {"name": "Bell Pepper", "quantity": 1, "unit": "piece"},
            {"name": "Onion", "quantity": 1, "unit": "piece"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Cumin Powder", "quantity": 0.5, "unit": "tsp"},
            {"name": "Smoked Paprika", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 10. Breakfast - Non-Veg
    {
        "name": "Avocado & Turkey Bacon Toast",
        "ingredients": [
            {"name": "Sourdough Bread", "quantity": 1, "unit": "slice"},
            {"name": "Turkey Bacon", "quantity": 35, "unit": "g"},
            {"name": "Avocado", "quantity": 1, "unit": "piece"},
            {"name": "Egg", "quantity": 1, "unit": "piece"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
            {"name": "Red Chili Flakes", "quantity": 0.25, "unit": "tsp"},
        ],
    },

    # 11. Lunch - Veg
    {
        "name": "Greek Quinoa Salad with Feta",
        "ingredients": [
            {"name": "Quinoa", "quantity": 65, "unit": "g"},
            {"name": "Cucumber", "quantity": 1, "unit": "piece"},
            {"name": "Tomato", "quantity": 1, "unit": "piece"},
            {"name": "Feta Cheese", "quantity": 40, "unit": "g"},
            {"name": "Red Onion", "quantity": 1, "unit": "piece"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Lemon", "quantity": 1, "unit": "piece"},
            {"name": "Dried Oregano", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
        ],
    },
    # 12. Lunch - Veg
    {
        "name": "Caprese Avocado Panini",
        "ingredients": [
            {"name": "Sourdough Bread", "quantity": 2, "unit": "slice"},
            {"name": "Mozzarella Cheese", "quantity": 45, "unit": "g"},
            {"name": "Tomato", "quantity": 1, "unit": "piece"},
            {"name": "Avocado", "quantity": 1, "unit": "piece"},
            {"name": "Fresh Basil", "quantity": 1, "unit": "bunch"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tsp"},
            {"name": "Balsamic Vinegar", "quantity": 1, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 13. Lunch - Veg
    {
        "name": "Black Bean & Sweet Potato Burrito Bowl",
        "ingredients": [
            {"name": "Black Beans", "quantity": 120, "unit": "g"},
            {"name": "Sweet Potato", "quantity": 1, "unit": "piece"},
            {"name": "Basmati Rice", "quantity": 60, "unit": "g"},
            {"name": "Bell Pepper", "quantity": 1, "unit": "piece"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Cumin Powder", "quantity": 0.5, "unit": "tsp"},
            {"name": "Smoked Paprika", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
        ],
    },
    # 14. Lunch - Veg
    {
        "name": "Creamy Mushroom Risotto",
        "ingredients": [
            {"name": "Arborio Rice", "quantity": 75, "unit": "g"},
            {"name": "Mushroom", "quantity": 90, "unit": "g"},
            {"name": "Parmesan Cheese", "quantity": 25, "unit": "g"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Onion", "quantity": 1, "unit": "piece"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 15. Lunch - Veg
    {
        "name": "Lentil & Roasted Veggie Salad",
        "ingredients": [
            {"name": "Red Lentils", "quantity": 70, "unit": "g"},
            {"name": "Zucchini", "quantity": 1, "unit": "piece"},
            {"name": "Bell Pepper", "quantity": 1, "unit": "piece"},
            {"name": "Red Onion", "quantity": 1, "unit": "piece"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Lemon", "quantity": 1, "unit": "piece"},
            {"name": "Garlic", "quantity": 1, "unit": "clove"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Dried Oregano", "quantity": 0.5, "unit": "tsp"},
        ],
    },
    # 16. Lunch - Non-Veg
    {
        "name": "Grilled Chicken & Avocado Salad",
        "ingredients": [
            {"name": "Chicken Breast", "quantity": 160, "unit": "g"},
            {"name": "Avocado", "quantity": 1, "unit": "piece"},
            {"name": "Romaine Lettuce", "quantity": 1, "unit": "bunch"},
            {"name": "Tomato", "quantity": 1, "unit": "piece"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Lemon", "quantity": 1, "unit": "piece"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 17. Lunch - Non-Veg
    {
        "name": "Tuna Salad Lettuce Wraps",
        "ingredients": [
            {"name": "Tuna", "quantity": 140, "unit": "g"},
            {"name": "Romaine Lettuce", "quantity": 1, "unit": "bunch"},
            {"name": "Greek Yogurt", "quantity": 2, "unit": "tbsp"},
            {"name": "Celery", "quantity": 1, "unit": "piece"},
            {"name": "Red Onion", "quantity": 1, "unit": "piece"},
            {"name": "Lemon", "quantity": 1, "unit": "piece"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 18. Lunch - Non-Veg
    {
        "name": "Turkey & Swiss Club Sandwich",
        "ingredients": [
            {"name": "Sourdough Bread", "quantity": 2, "unit": "slice"},
            {"name": "Ground Turkey", "quantity": 120, "unit": "g"},
            {"name": "Cheddar Cheese", "quantity": 25, "unit": "g"},
            {"name": "Tomato", "quantity": 1, "unit": "piece"},
            {"name": "Romaine Lettuce", "quantity": 1, "unit": "bunch"},
            {"name": "Butter", "quantity": 1, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 19. Lunch - Non-Veg
    {
        "name": "Lemon Garlic Shrimp Salad",
        "ingredients": [
            {"name": "Shrimp", "quantity": 150, "unit": "g"},
            {"name": "Romaine Lettuce", "quantity": 1, "unit": "bunch"},
            {"name": "Cucumber", "quantity": 1, "unit": "piece"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Lemon", "quantity": 1, "unit": "piece"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 20. Lunch - Non-Veg
    {
        "name": "Chicken Shawarma Pita Wrap",
        "ingredients": [
            {"name": "Chicken Breast", "quantity": 150, "unit": "g"},
            {"name": "Pita Bread", "quantity": 1, "unit": "piece"},
            {"name": "Cucumber", "quantity": 1, "unit": "piece"},
            {"name": "Tomato", "quantity": 1, "unit": "piece"},
            {"name": "Greek Yogurt", "quantity": 2, "unit": "tbsp"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tsp"},
            {"name": "Garlic", "quantity": 1, "unit": "clove"},
            {"name": "Cumin Powder", "quantity": 0.5, "unit": "tsp"},
            {"name": "Smoked Paprika", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
        ],
    },

    # 21. Dinner - Veg
    {
        "name": "Palak Paneer with Basmati Rice",
        "ingredients": [
            {"name": "Paneer", "quantity": 110, "unit": "g"},
            {"name": "Fresh Spinach", "quantity": 120, "unit": "g"},
            {"name": "Basmati Rice", "quantity": 70, "unit": "g"},
            {"name": "Tomato", "quantity": 1, "unit": "piece"},
            {"name": "Onion", "quantity": 1, "unit": "piece"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Garam Masala", "quantity": 0.5, "unit": "tsp"},
            {"name": "Cumin Seeds", "quantity": 0.5, "unit": "tsp"},
            {"name": "Turmeric Powder", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
        ],
    },
    # 22. Dinner - Veg
    {
        "name": "Thai Green Vegetable Curry",
        "ingredients": [
            {"name": "Coconut Milk", "quantity": 150, "unit": "ml"},
            {"name": "Firm Tofu", "quantity": 90, "unit": "g"},
            {"name": "Broccoli", "quantity": 1, "unit": "bunch"},
            {"name": "Bell Pepper", "quantity": 1, "unit": "piece"},
            {"name": "Jasmine Rice", "quantity": 70, "unit": "g"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Soy Sauce", "quantity": 1, "unit": "tbsp"},
            {"name": "Brown Sugar", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
        ],
    },
    # 23. Dinner - Veg
    {
        "name": "Eggplant Parmesan Bake",
        "ingredients": [
            {"name": "Eggplant", "quantity": 1, "unit": "piece"},
            {"name": "Marinara Sauce", "quantity": 120, "unit": "g"},
            {"name": "Mozzarella Cheese", "quantity": 50, "unit": "g"},
            {"name": "Parmesan Cheese", "quantity": 25, "unit": "g"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Fresh Basil", "quantity": 1, "unit": "bunch"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 24. Dinner - Veg
    {
        "name": "Black Bean & Corn Quesadilla",
        "ingredients": [
            {"name": "Tortilla Wrap", "quantity": 1, "unit": "piece"},
            {"name": "Black Beans", "quantity": 80, "unit": "g"},
            {"name": "Sweet Corn", "quantity": 50, "unit": "g"},
            {"name": "Cheddar Cheese", "quantity": 35, "unit": "g"},
            {"name": "Bell Pepper", "quantity": 1, "unit": "piece"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tsp"},
            {"name": "Cumin Powder", "quantity": 0.25, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 25. Dinner - Veg
    {
        "name": "Mushroom & Garlic Butter Spaghetti",
        "ingredients": [
            {"name": "Spaghetti", "quantity": 85, "unit": "g"},
            {"name": "Mushroom", "quantity": 90, "unit": "g"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp"},
            {"name": "Garlic", "quantity": 3, "unit": "clove"},
            {"name": "Parmesan Cheese", "quantity": 20, "unit": "g"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tsp"},
            {"name": "Fresh Parsley", "quantity": 1, "unit": "bunch"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 26. Dinner - Non-Veg
    {
        "name": "Grilled Sirloin Steak with Roasted Asparagus",
        "ingredients": [
            {"name": "Sirloin Steak", "quantity": 180, "unit": "g"},
            {"name": "Asparagus", "quantity": 1, "unit": "bunch"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.5, "unit": "tsp"},
        ],
    },
    # 27. Dinner - Non-Veg
    {
        "name": "Baked Cod with Lemon Herb Butter",
        "ingredients": [
            {"name": "Cod Fillet", "quantity": 170, "unit": "g"},
            {"name": "Asparagus", "quantity": 1, "unit": "bunch"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp"},
            {"name": "Lemon", "quantity": 1, "unit": "piece"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Fresh Parsley", "quantity": 1, "unit": "bunch"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 28. Dinner - Non-Veg
    {
        "name": "Butter Chicken with Basmati Rice",
        "ingredients": [
            {"name": "Chicken Breast", "quantity": 160, "unit": "g"},
            {"name": "Basmati Rice", "quantity": 75, "unit": "g"},
            {"name": "Tomato", "quantity": 2, "unit": "piece"},
            {"name": "Heavy Cream", "quantity": 30, "unit": "ml"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp"},
            {"name": "Onion", "quantity": 1, "unit": "piece"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Garam Masala", "quantity": 0.5, "unit": "tsp"},
            {"name": "Turmeric Powder", "quantity": 0.25, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
        ],
    },
    # 29. Dinner - Non-Veg
    {
        "name": "Honey Garlic Glazed Salmon",
        "ingredients": [
            {"name": "Salmon Fillet", "quantity": 160, "unit": "g"},
            {"name": "Jasmine Rice", "quantity": 70, "unit": "g"},
            {"name": "Broccoli", "quantity": 1, "unit": "bunch"},
            {"name": "Honey", "quantity": 1, "unit": "tbsp"},
            {"name": "Soy Sauce", "quantity": 1, "unit": "tbsp"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.25, "unit": "tsp"},
        ],
    },
    # 30. Dinner - Non-Veg
    {
        "name": "Turkey Meatballs with Marinara Pasta",
        "ingredients": [
            {"name": "Ground Turkey", "quantity": 140, "unit": "g"},
            {"name": "Spaghetti", "quantity": 80, "unit": "g"},
            {"name": "Marinara Sauce", "quantity": 100, "unit": "g"},
            {"name": "Parmesan Cheese", "quantity": 20, "unit": "g"},
            {"name": "Garlic", "quantity": 2, "unit": "clove"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Dried Oregano", "quantity": 0.5, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Black Pepper", "quantity": 0.25, "unit": "tsp"},
        ],
    },
]


def seed_recipes_if_empty(db: Session) -> int:
    """Preload standard recipes into the database (seeds any missing recipes)."""
    if os.getenv("TESTING") == "1":
        return 0

    existing_names = set(name.strip().lower() for name in db.scalars(select(Recipe.name)).all())
    added = 0
    for item in PRELOADED_RECIPES:
        if item["name"].strip().lower() not in existing_names:
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

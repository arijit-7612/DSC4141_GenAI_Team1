"""Deterministic nutrition calculation and dietary analysis engine.

Uses verified food composition data per 100g and culinary density/weight conversions.
Calculates macronutrients, micronutrients, dietary labels (Vegan, Vegetarian, Dairy-Free,
High-Protein, Gluten-Free), and common allergen detection.
"""

from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.models.recipe import Recipe

# Allergen Constants (Big 8 / Standard)
ALLERGEN_MILK = "Milk"
ALLERGEN_EGGS = "Eggs"
ALLERGEN_WHEAT = "Wheat / Gluten"
ALLERGEN_SOY = "Soy"
ALLERGEN_PEANUTS = "Peanuts"
ALLERGEN_TREE_NUTS = "Tree Nuts"
ALLERGEN_FISH = "Fish"
ALLERGEN_SHELLFISH = "Shellfish"

# Food composition data per 100g
# Values: (cal, protein_g, carbs_g, fat_g, fiber_g, sugar_g, sat_fat_g, sodium_mg, allergens, is_vegan, is_vegetarian, is_dairy_free, is_gluten_free)
FOOD_COMPOSITION_PER_100G: dict[str, dict[str, Any]] = {
    "rolled oats": {
        "calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9,
        "fiber": 10.6, "sugar": 0.8, "sat_fat": 1.2, "sodium": 2.0,
        "allergens": [ALLERGEN_WHEAT], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": False,
    },
    "milk": {
        "calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3,
        "fiber": 0.0, "sugar": 5.1, "sat_fat": 1.9, "sodium": 43.0,
        "allergens": [ALLERGEN_MILK], "is_vegan": False, "is_vegetarian": True, "is_dairy_free": False, "is_gluten_free": True,
    },
    "mixed berries": {
        "calories": 57, "protein": 0.7, "carbs": 14.5, "fat": 0.3,
        "fiber": 2.4, "sugar": 10.0, "sat_fat": 0.0, "sodium": 1.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "honey": {
        "calories": 304, "protein": 0.3, "carbs": 82.4, "fat": 0.0,
        "fiber": 0.2, "sugar": 82.1, "sat_fat": 0.0, "sodium": 4.0,
        "allergens": [], "is_vegan": False, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "brown sugar": {
        "calories": 380, "protein": 0.1, "carbs": 98.0, "fat": 0.0,
        "fiber": 0.0, "sugar": 97.0, "sat_fat": 0.0, "sodium": 28.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "white sugar": {
        "calories": 387, "protein": 0.0, "carbs": 100.0, "fat": 0.0,
        "fiber": 0.0, "sugar": 100.0, "sat_fat": 0.0, "sodium": 1.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "cinnamon powder": {
        "calories": 247, "protein": 4.0, "carbs": 81.0, "fat": 1.2,
        "fiber": 53.0, "sugar": 2.2, "sat_fat": 0.3, "sodium": 10.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "chia seeds": {
        "calories": 486, "protein": 16.5, "carbs": 42.1, "fat": 30.7,
        "fiber": 34.4, "sugar": 0.0, "sat_fat": 3.3, "sodium": 16.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "salt": {
        "calories": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 0.0, "sodium": 38758.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "black pepper": {
        "calories": 251, "protein": 10.4, "carbs": 64.0, "fat": 3.3,
        "fiber": 25.3, "sugar": 0.6, "sat_fat": 1.4, "sodium": 20.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "red chili flakes": {
        "calories": 318, "protein": 12.0, "carbs": 56.6, "fat": 17.3,
        "fiber": 27.2, "sugar": 10.3, "sat_fat": 3.3, "sodium": 30.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "sourdough bread": {
        "calories": 260, "protein": 9.0, "carbs": 49.0, "fat": 3.0,
        "fiber": 2.5, "sugar": 2.0, "sat_fat": 0.5, "sodium": 510.0,
        "allergens": [ALLERGEN_WHEAT], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": False,
    },
    "avocado": {
        "calories": 160, "protein": 2.0, "carbs": 8.5, "fat": 14.7,
        "fiber": 6.7, "sugar": 0.7, "sat_fat": 2.1, "sodium": 7.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "egg": {
        "calories": 143, "protein": 12.6, "carbs": 0.7, "fat": 9.5,
        "fiber": 0.0, "sugar": 0.4, "sat_fat": 3.1, "sodium": 142.0,
        "allergens": [ALLERGEN_EGGS], "is_vegan": False, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "lemon": {
        "calories": 29, "protein": 1.1, "carbs": 9.3, "fat": 0.3,
        "fiber": 2.8, "sugar": 2.5, "sat_fat": 0.0, "sodium": 2.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "olive oil": {
        "calories": 884, "protein": 0.0, "carbs": 0.0, "fat": 100.0,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 14.0, "sodium": 2.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "greek yogurt": {
        "calories": 97, "protein": 9.0, "carbs": 3.6, "fat": 5.0,
        "fiber": 0.0, "sugar": 3.6, "sat_fat": 3.3, "sodium": 47.0,
        "allergens": [ALLERGEN_MILK], "is_vegan": False, "is_vegetarian": True, "is_dairy_free": False, "is_gluten_free": True,
    },
    "granola": {
        "calories": 471, "protein": 10.0, "carbs": 64.0, "fat": 20.0,
        "fiber": 5.0, "sugar": 29.0, "sat_fat": 3.0, "sodium": 294.0,
        "allergens": [ALLERGEN_WHEAT], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": False,
    },
    "banana": {
        "calories": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3,
        "fiber": 2.6, "sugar": 12.2, "sat_fat": 0.1, "sodium": 1.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "all-purpose flour": {
        "calories": 364, "protein": 10.3, "carbs": 76.3, "fat": 1.0,
        "fiber": 2.7, "sugar": 0.3, "sat_fat": 0.2, "sodium": 2.0,
        "allergens": [ALLERGEN_WHEAT], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": False,
    },
    "butter": {
        "calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81.1,
        "fiber": 0.0, "sugar": 0.1, "sat_fat": 51.4, "sodium": 576.0,
        "allergens": [ALLERGEN_MILK], "is_vegan": False, "is_vegetarian": True, "is_dairy_free": False, "is_gluten_free": True,
    },
    "baking powder": {
        "calories": 53, "protein": 0.0, "carbs": 27.7, "fat": 0.0,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 0.0, "sodium": 10600.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "vanilla extract": {
        "calories": 288, "protein": 0.1, "carbs": 12.7, "fat": 0.1,
        "fiber": 0.0, "sugar": 12.6, "sat_fat": 0.0, "sodium": 9.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "fresh spinach": {
        "calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4,
        "fiber": 2.2, "sugar": 0.4, "sat_fat": 0.1, "sodium": 79.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "mushroom": {
        "calories": 22, "protein": 3.1, "carbs": 3.3, "fat": 0.3,
        "fiber": 1.0, "sugar": 2.0, "sat_fat": 0.0, "sodium": 5.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "cheddar cheese": {
        "calories": 403, "protein": 24.9, "carbs": 1.3, "fat": 33.1,
        "fiber": 0.0, "sugar": 0.5, "sat_fat": 21.1, "sodium": 621.0,
        "allergens": [ALLERGEN_MILK], "is_vegan": False, "is_vegetarian": True, "is_dairy_free": False, "is_gluten_free": True,
    },
    "chickpeas": {
        "calories": 164, "protein": 8.9, "carbs": 27.4, "fat": 2.6,
        "fiber": 7.6, "sugar": 4.8, "sat_fat": 0.3, "sodium": 387.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "cucumber": {
        "calories": 15, "protein": 0.7, "carbs": 3.6, "fat": 0.1,
        "fiber": 0.5, "sugar": 1.7, "sat_fat": 0.0, "sodium": 2.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "tomato": {
        "calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2,
        "fiber": 1.2, "sugar": 2.6, "sat_fat": 0.0, "sodium": 5.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "red onion": {
        "calories": 40, "protein": 1.1, "carbs": 9.3, "fat": 0.1,
        "fiber": 1.7, "sugar": 4.2, "sat_fat": 0.0, "sodium": 4.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "onion": {
        "calories": 40, "protein": 1.1, "carbs": 9.3, "fat": 0.1,
        "fiber": 1.7, "sugar": 4.2, "sat_fat": 0.0, "sodium": 4.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "feta cheese": {
        "calories": 264, "protein": 14.2, "carbs": 4.1, "fat": 21.3,
        "fiber": 0.0, "sugar": 4.1, "sat_fat": 14.9, "sodium": 917.0,
        "allergens": [ALLERGEN_MILK], "is_vegan": False, "is_vegetarian": True, "is_dairy_free": False, "is_gluten_free": True,
    },
    "dried oregano": {
        "calories": 265, "protein": 9.0, "carbs": 68.9, "fat": 4.3,
        "fiber": 42.8, "sugar": 4.1, "sat_fat": 1.6, "sodium": 25.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "chicken breast": {
        "calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 1.0, "sodium": 74.0,
        "allergens": [], "is_vegan": False, "is_vegetarian": False, "is_dairy_free": True, "is_gluten_free": True,
    },
    "romaine lettuce": {
        "calories": 17, "protein": 1.2, "carbs": 3.3, "fat": 0.3,
        "fiber": 2.1, "sugar": 1.2, "sat_fat": 0.0, "sodium": 8.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "parmesan cheese": {
        "calories": 431, "protein": 38.4, "carbs": 4.1, "fat": 28.6,
        "fiber": 0.0, "sugar": 0.9, "sat_fat": 16.4, "sodium": 1529.0,
        "allergens": [ALLERGEN_MILK], "is_vegan": False, "is_vegetarian": True, "is_dairy_free": False, "is_gluten_free": True,
    },
    "croutons": {
        "calories": 407, "protein": 12.0, "carbs": 68.0, "fat": 9.0,
        "fiber": 4.5, "sugar": 3.0, "sat_fat": 1.8, "sodium": 698.0,
        "allergens": [ALLERGEN_WHEAT], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": False,
    },
    "caesar dressing": {
        "calories": 470, "protein": 2.1, "carbs": 4.2, "fat": 50.0,
        "fiber": 0.2, "sugar": 3.0, "sat_fat": 8.5, "sodium": 1140.0,
        "allergens": [ALLERGEN_MILK, ALLERGEN_EGGS, ALLERGEN_FISH], "is_vegan": False, "is_vegetarian": False, "is_dairy_free": False, "is_gluten_free": True,
    },
    "garlic": {
        "calories": 149, "protein": 6.4, "carbs": 33.1, "fat": 0.5,
        "fiber": 2.1, "sugar": 1.0, "sat_fat": 0.1, "sodium": 17.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "quinoa": {
        "calories": 368, "protein": 14.1, "carbs": 64.2, "fat": 6.1,
        "fiber": 7.0, "sugar": 0.0, "sat_fat": 0.7, "sodium": 5.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "bell pepper": {
        "calories": 31, "protein": 1.0, "carbs": 6.0, "fat": 0.3,
        "fiber": 2.1, "sugar": 4.2, "sat_fat": 0.0, "sodium": 4.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "zucchini": {
        "calories": 17, "protein": 1.2, "carbs": 3.1, "fat": 0.3,
        "fiber": 1.0, "sugar": 2.5, "sat_fat": 0.1, "sodium": 8.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "smoked paprika": {
        "calories": 282, "protein": 14.1, "carbs": 54.0, "fat": 12.8,
        "fiber": 34.9, "sugar": 10.3, "sat_fat": 2.1, "sodium": 68.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "paneer": {
        "calories": 296, "protein": 18.3, "carbs": 4.5, "fat": 22.8,
        "fiber": 0.0, "sugar": 2.5, "sat_fat": 14.2, "sodium": 18.0,
        "allergens": [ALLERGEN_MILK], "is_vegan": False, "is_vegetarian": True, "is_dairy_free": False, "is_gluten_free": True,
    },
    "tortilla wrap": {
        "calories": 297, "protein": 8.0, "carbs": 50.0, "fat": 7.0,
        "fiber": 3.5, "sugar": 2.0, "sat_fat": 1.5, "sodium": 480.0,
        "allergens": [ALLERGEN_WHEAT], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": False,
    },
    "ginger garlic paste": {
        "calories": 80, "protein": 3.0, "carbs": 14.0, "fat": 1.0,
        "fiber": 2.0, "sugar": 1.0, "sat_fat": 0.2, "sodium": 800.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "garam masala": {
        "calories": 379, "protein": 15.0, "carbs": 66.0, "fat": 15.0,
        "fiber": 25.0, "sugar": 2.0, "sat_fat": 2.0, "sodium": 50.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "red chili powder": {
        "calories": 282, "protein": 13.0, "carbs": 50.0, "fat": 14.0,
        "fiber": 34.0, "sugar": 7.0, "sat_fat": 2.5, "sodium": 30.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "penne pasta": {
        "calories": 355, "protein": 13.0, "carbs": 71.0, "fat": 1.5,
        "fiber": 3.2, "sugar": 3.2, "sat_fat": 0.3, "sodium": 6.0,
        "allergens": [ALLERGEN_WHEAT], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": False,
    },
    "fresh basil": {
        "calories": 23, "protein": 3.2, "carbs": 2.7, "fat": 0.6,
        "fiber": 1.6, "sugar": 0.3, "sat_fat": 0.0, "sodium": 4.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "heavy cream": {
        "calories": 340, "protein": 2.8, "carbs": 2.7, "fat": 36.1,
        "fiber": 0.0, "sugar": 2.9, "sat_fat": 23.0, "sodium": 38.0,
        "allergens": [ALLERGEN_MILK], "is_vegan": False, "is_vegetarian": True, "is_dairy_free": False, "is_gluten_free": True,
    },
    "broccoli": {
        "calories": 34, "protein": 2.8, "carbs": 6.6, "fat": 0.4,
        "fiber": 2.6, "sugar": 1.7, "sat_fat": 0.0, "sodium": 33.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "carrot": {
        "calories": 41, "protein": 0.9, "carbs": 9.6, "fat": 0.2,
        "fiber": 2.8, "sugar": 4.7, "sat_fat": 0.0, "sodium": 69.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "soy sauce": {
        "calories": 53, "protein": 8.1, "carbs": 4.9, "fat": 0.6,
        "fiber": 0.8, "sugar": 0.4, "sat_fat": 0.1, "sodium": 5493.0,
        "allergens": [ALLERGEN_SOY, ALLERGEN_WHEAT], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": False,
    },
    "sesame oil": {
        "calories": 884, "protein": 0.0, "carbs": 0.0, "fat": 100.0,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 14.2, "sodium": 0.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "red lentils": {
        "calories": 343, "protein": 24.6, "carbs": 63.4, "fat": 1.1,
        "fiber": 10.8, "sugar": 2.0, "sat_fat": 0.2, "sodium": 6.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "turmeric powder": {
        "calories": 354, "protein": 7.8, "carbs": 64.9, "fat": 9.9,
        "fiber": 21.1, "sugar": 3.2, "sat_fat": 3.1, "sodium": 38.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "cumin seeds": {
        "calories": 375, "protein": 17.8, "carbs": 44.2, "fat": 22.3,
        "fiber": 10.5, "sugar": 2.3, "sat_fat": 1.5, "sodium": 168.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "salmon fillet": {
        "calories": 208, "protein": 20.4, "carbs": 0.0, "fat": 13.4,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 3.1, "sodium": 59.0,
        "allergens": [ALLERGEN_FISH], "is_vegan": False, "is_vegetarian": False, "is_dairy_free": True, "is_gluten_free": True,
    },
    "asparagus": {
        "calories": 20, "protein": 2.2, "carbs": 3.9, "fat": 0.1,
        "fiber": 2.1, "sugar": 1.9, "sat_fat": 0.0, "sodium": 2.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "basmati rice": {
        "calories": 365, "protein": 7.1, "carbs": 80.0, "fat": 0.7,
        "fiber": 1.3, "sugar": 0.1, "sat_fat": 0.2, "sodium": 5.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "firm tofu": {
        "calories": 83, "protein": 10.0, "carbs": 1.2, "fat": 5.3,
        "fiber": 1.0, "sugar": 0.5, "sat_fat": 0.8, "sodium": 10.0,
        "allergens": [ALLERGEN_SOY], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "green onion": {
        "calories": 32, "protein": 1.8, "carbs": 7.3, "fat": 0.2,
        "fiber": 2.6, "sugar": 2.3, "sat_fat": 0.0, "sodium": 16.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "peanut butter": {
        "calories": 588, "protein": 25.0, "carbs": 20.0, "fat": 50.0,
        "fiber": 6.0, "sugar": 9.0, "sat_fat": 10.0, "sodium": 426.0,
        "allergens": [ALLERGEN_PEANUTS], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "peanut": {
        "calories": 567, "protein": 25.8, "carbs": 16.1, "fat": 49.2,
        "fiber": 8.5, "sugar": 4.7, "sat_fat": 6.8, "sodium": 18.0,
        "allergens": [ALLERGEN_PEANUTS], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "white rice": {
        "calories": 365, "protein": 7.1, "carbs": 80.0, "fat": 0.7,
        "fiber": 1.3, "sugar": 0.1, "sat_fat": 0.2, "sodium": 5.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "rice": {
        "calories": 365, "protein": 7.1, "carbs": 80.0, "fat": 0.7,
        "fiber": 1.3, "sugar": 0.1, "sat_fat": 0.2, "sodium": 5.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "potato": {
        "calories": 77, "protein": 2.0, "carbs": 17.5, "fat": 0.1,
        "fiber": 2.2, "sugar": 0.8, "sat_fat": 0.0, "sodium": 6.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "pasta": {
        "calories": 355, "protein": 13.0, "carbs": 71.0, "fat": 1.5,
        "fiber": 3.2, "sugar": 3.2, "sat_fat": 0.3, "sodium": 6.0,
        "allergens": [ALLERGEN_WHEAT], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": False,
    },
    "bread": {
        "calories": 265, "protein": 9.0, "carbs": 49.0, "fat": 3.2,
        "fiber": 2.7, "sugar": 5.0, "sat_fat": 0.7, "sodium": 490.0,
        "allergens": [ALLERGEN_WHEAT], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": False,
    },
    "shrimp": {
        "calories": 99, "protein": 24.0, "carbs": 0.2, "fat": 0.3,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 0.1, "sodium": 111.0,
        "allergens": [ALLERGEN_SHELLFISH], "is_vegan": False, "is_vegetarian": False, "is_dairy_free": True, "is_gluten_free": True,
    },
    "walnut": {
        "calories": 654, "protein": 15.2, "carbs": 13.7, "fat": 65.2,
        "fiber": 6.7, "sugar": 2.6, "sat_fat": 6.1, "sodium": 2.0,
        "allergens": [ALLERGEN_TREE_NUTS], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "almond": {
        "calories": 579, "protein": 21.2, "carbs": 21.6, "fat": 49.9,
        "fiber": 12.5, "sugar": 4.4, "sat_fat": 3.8, "sodium": 1.0,
        "allergens": [ALLERGEN_TREE_NUTS], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "blueberries": {
        "calories": 57, "protein": 0.7, "carbs": 14.5, "fat": 0.3,
        "fiber": 2.4, "sugar": 10.0, "sat_fat": 0.0, "sodium": 1.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "almond milk": {
        "calories": 15, "protein": 0.6, "carbs": 0.6, "fat": 1.1,
        "fiber": 0.2, "sugar": 0.0, "sat_fat": 0.1, "sodium": 68.0,
        "allergens": [ALLERGEN_TREE_NUTS], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "apple": {
        "calories": 52, "protein": 0.3, "carbs": 13.8, "fat": 0.2,
        "fiber": 2.4, "sugar": 10.4, "sat_fat": 0.0, "sodium": 1.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "maple syrup": {
        "calories": 260, "protein": 0.0, "carbs": 67.0, "fat": 0.0,
        "fiber": 0.0, "sugar": 60.0, "sat_fat": 0.0, "sodium": 12.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "smoked salmon": {
        "calories": 117, "protein": 18.3, "carbs": 0.0, "fat": 4.3,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 0.9, "sodium": 784.0,
        "allergens": [ALLERGEN_FISH], "is_vegan": False, "is_vegetarian": False, "is_dairy_free": True, "is_gluten_free": True,
    },
    "bacon": {
        "calories": 541, "protein": 37.0, "carbs": 1.4, "fat": 42.0,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 14.0, "sodium": 1717.0,
        "allergens": [], "is_vegan": False, "is_vegetarian": False, "is_dairy_free": True, "is_gluten_free": True,
    },
    "turkey bacon": {
        "calories": 368, "protein": 30.0, "carbs": 3.0, "fat": 26.0,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 7.5, "sodium": 1950.0,
        "allergens": [], "is_vegan": False, "is_vegetarian": False, "is_dairy_free": True, "is_gluten_free": True,
    },
    "ground turkey": {
        "calories": 189, "protein": 27.0, "carbs": 0.0, "fat": 8.5,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 2.4, "sodium": 85.0,
        "allergens": [], "is_vegan": False, "is_vegetarian": False, "is_dairy_free": True, "is_gluten_free": True,
    },
    "sirloin steak": {
        "calories": 206, "protein": 29.0, "carbs": 0.0, "fat": 9.2,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 3.8, "sodium": 56.0,
        "allergens": [], "is_vegan": False, "is_vegetarian": False, "is_dairy_free": True, "is_gluten_free": True,
    },
    "cod fillet": {
        "calories": 82, "protein": 17.8, "carbs": 0.0, "fat": 0.7,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 0.1, "sodium": 54.0,
        "allergens": [ALLERGEN_FISH], "is_vegan": False, "is_vegetarian": False, "is_dairy_free": True, "is_gluten_free": True,
    },
    "tuna": {
        "calories": 132, "protein": 28.0, "carbs": 0.0, "fat": 1.3,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 0.3, "sodium": 333.0,
        "allergens": [ALLERGEN_FISH], "is_vegan": False, "is_vegetarian": False, "is_dairy_free": True, "is_gluten_free": True,
    },
    "mozzarella cheese": {
        "calories": 280, "protein": 28.0, "carbs": 3.1, "fat": 17.1,
        "fiber": 0.0, "sugar": 1.0, "sat_fat": 10.9, "sodium": 627.0,
        "allergens": [ALLERGEN_MILK], "is_vegan": False, "is_vegetarian": True, "is_dairy_free": False, "is_gluten_free": True,
    },
    "sweet potato": {
        "calories": 86, "protein": 1.6, "carbs": 20.1, "fat": 0.1,
        "fiber": 3.0, "sugar": 4.2, "sat_fat": 0.0, "sodium": 55.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "black beans": {
        "calories": 132, "protein": 8.9, "carbs": 23.7, "fat": 0.5,
        "fiber": 8.7, "sugar": 0.3, "sat_fat": 0.1, "sodium": 1.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "sweet corn": {
        "calories": 86, "protein": 3.2, "carbs": 19.0, "fat": 1.2,
        "fiber": 2.7, "sugar": 6.3, "sat_fat": 0.2, "sodium": 15.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "eggplant": {
        "calories": 25, "protein": 1.0, "carbs": 6.0, "fat": 0.2,
        "fiber": 3.0, "sugar": 3.5, "sat_fat": 0.0, "sodium": 2.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "marinara sauce": {
        "calories": 51, "protein": 1.7, "carbs": 7.8, "fat": 1.5,
        "fiber": 1.5, "sugar": 4.5, "sat_fat": 0.2, "sodium": 430.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "coconut milk": {
        "calories": 197, "protein": 2.0, "carbs": 3.3, "fat": 21.3,
        "fiber": 0.0, "sugar": 0.0, "sat_fat": 18.9, "sodium": 15.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "pita bread": {
        "calories": 275, "protein": 9.1, "carbs": 55.7, "fat": 1.2,
        "fiber": 2.2, "sugar": 1.7, "sat_fat": 0.2, "sodium": 536.0,
        "allergens": [ALLERGEN_WHEAT], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": False,
    },
    "arborio rice": {
        "calories": 365, "protein": 7.0, "carbs": 80.0, "fat": 0.7,
        "fiber": 1.3, "sugar": 0.1, "sat_fat": 0.2, "sodium": 5.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "jasmine rice": {
        "calories": 365, "protein": 7.0, "carbs": 80.0, "fat": 0.7,
        "fiber": 1.3, "sugar": 0.1, "sat_fat": 0.2, "sodium": 5.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "spaghetti": {
        "calories": 355, "protein": 13.0, "carbs": 71.0, "fat": 1.5,
        "fiber": 3.2, "sugar": 3.2, "sat_fat": 0.3, "sodium": 6.0,
        "allergens": [ALLERGEN_WHEAT], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": False,
    },
    "fresh parsley": {
        "calories": 36, "protein": 3.0, "carbs": 6.3, "fat": 0.8,
        "fiber": 3.3, "sugar": 0.9, "sat_fat": 0.1, "sodium": 56.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "celery": {
        "calories": 14, "protein": 0.7, "carbs": 3.0, "fat": 0.2,
        "fiber": 1.6, "sugar": 1.3, "sat_fat": 0.1, "sodium": 80.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "balsamic vinegar": {
        "calories": 88, "protein": 0.5, "carbs": 17.0, "fat": 0.0,
        "fiber": 0.0, "sugar": 15.0, "sat_fat": 0.0, "sodium": 23.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
    "cumin powder": {
        "calories": 375, "protein": 17.8, "carbs": 44.2, "fat": 22.3,
        "fiber": 10.5, "sugar": 2.3, "sat_fat": 1.5, "sodium": 168.0,
        "allergens": [], "is_vegan": True, "is_vegetarian": True, "is_dairy_free": True, "is_gluten_free": True,
    },
}

# Standard ingredient weight per piece / bunch / slice
ITEM_UNIT_WEIGHT_IN_GRAMS: dict[str, dict[str, float]] = {
    "piece": {
        "egg": 50.0,
        "banana": 118.0,
        "avocado": 150.0,
        "lemon": 60.0,
        "lime": 45.0,
        "tomato": 120.0,
        "cucumber": 150.0,
        "onion": 110.0,
        "red onion": 110.0,
        "bell pepper": 120.0,
        "zucchini": 180.0,
        "carrot": 60.0,
        "tortilla wrap": 60.0,
        "apple": 180.0,
        "sweet potato": 180.0,
        "eggplant": 250.0,
        "pita bread": 60.0,
        "celery": 40.0,
        "default": 100.0,
    },
    "clove": {"default": 3.0},
    "slice": {"default": 35.0},
    "bunch": {
        "broccoli": 250.0,
        "romaine lettuce": 200.0,
        "fresh basil": 25.0,
        "green onion": 50.0,
        "asparagus": 180.0,
        "spinach": 150.0,
        "default": 100.0,
    },
    "can": {
        "chickpeas": 240.0,
        "canned tomato": 400.0,
        "default": 400.0,
    },
}


def _get_grams_for_ingredient(ingredient_name: str, quantity: float, unit: str) -> float:
    """Deterministically convert any recipe ingredient quantity + unit into grams."""
    u = unit.strip().lower()
    name = ingredient_name.strip().lower()

    if u in ("g", "ml"):
        return quantity
    if u in ("kg", "l"):
        return quantity * 1000.0
    if u == "tsp":
        return quantity * 5.0
    if u == "tbsp":
        return quantity * 15.0
    if u == "cup":
        return quantity * 240.0

    # Specific piece / slice / bunch / can lookups
    if u in ITEM_UNIT_WEIGHT_IN_GRAMS:
        table = ITEM_UNIT_WEIGHT_IN_GRAMS[u]
        for key, grams in table.items():
            if key != "default" and key in name:
                return quantity * grams
        return quantity * table.get("default", 100.0)

    return quantity * 100.0  # Reasonable fallback


CACHE_FILE = Path(__file__).resolve().parent.parent.parent / "usda_cache.json"
_PERSISTENT_CACHE: dict[str, dict[str, Any]] = {}


def _load_cache() -> None:
    global _PERSISTENT_CACHE
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _PERSISTENT_CACHE = json.load(f)
                FOOD_COMPOSITION_PER_100G.update(_PERSISTENT_CACHE)
        except Exception:
            _PERSISTENT_CACHE = {}


def _save_cached_food(clean_name: str, food_data: dict[str, Any]) -> None:
    _PERSISTENT_CACHE[clean_name] = food_data
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_PERSISTENT_CACHE, f, indent=2)
    except Exception:
        pass


_load_cache()


def fetch_usda_nutrition(ingredient_name: str) -> dict[str, Any] | None:
    """Fetch verified food composition data per 100g from USDA FoodData Central."""
    clean = ingredient_name.strip().lower()
    cleaned_query = re.sub(
        r"\b(fresh|organic|raw|cooked|diced|chopped|sliced|canned|frozen|minced|grated|peeled)\b",
        "",
        clean,
    ).strip()
    if not cleaned_query:
        cleaned_query = clean

    api_key = os.getenv("USDA_API_KEY", "z8GHgPfFjCK8mKd8TTBmG9GMdJcnJPf96kDPzLgm")

    # Try Foundation & SR Legacy first (highest lab accuracy), then fallback to all types
    queries = [
        f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={urllib.parse.quote(cleaned_query)}&dataType=Foundation,SR%20Legacy&requireAllWords=true&pageSize=1",
        f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={urllib.parse.quote(cleaned_query)}&requireAllWords=true&pageSize=1",
    ]

    food = None
    for url in queries:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SmartBite/1.0"})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode("utf-8"))
                foods = data.get("foods", [])
                if foods:
                    food = foods[0]
                    break
        except Exception:
            continue

    if not food:
        return None

    # Parse nutrients per 100g
    calories = 0.0
    protein = 0.0
    carbs = 0.0
    fat = 0.0
    fiber = 0.0
    sugar = 0.0
    sat_fat = 0.0
    sodium = 0.0

    for n in food.get("foodNutrients", []):
        name = (n.get("nutrientName") or "").lower()
        val = float(n.get("value") or 0.0)
        unit = (n.get("unitName") or "").upper()
        num = str(n.get("nutrientNumber") or "")

        if "energy" in name and (unit == "KCAL" or num == "208"):
            calories = val
        elif "protein" in name or num == "203":
            protein = val
        elif "carbohydrate" in name or num == "205":
            carbs = val
        elif "total lipid" in name or num == "204" or (name == "fat" and unit == "G"):
            fat = val
        elif "fiber" in name or num == "291":
            fiber = val
        elif "sugar" in name or num == "269":
            sugar = val
        elif ("saturated" in name and unit == "G") or num == "606":
            sat_fat = val
        elif ("sodium" in name and unit == "MG") or num == "307":
            sodium = val

    # If calories not found explicitly, calculate via Atwater factors
    if calories <= 0 and (protein > 0 or carbs > 0 or fat > 0):
        calories = round(protein * 4.0 + carbs * 4.0 + fat * 9.0)

    # Detect allergens from description and ingredient list
    text_to_check = f"{clean} {food.get('description', '')} {food.get('ingredients', '')}".lower()
    allergens: list[str] = []
    if any(k in text_to_check for k in ["milk", "cheese", "butter", "yogurt", "cream", "whey", "casein", "ghee"]):
        allergens.append(ALLERGEN_MILK)
    if any(k in text_to_check for k in ["egg", "albumen", "mayonnaise"]):
        allergens.append(ALLERGEN_EGGS)
    if any(k in text_to_check for k in ["wheat", "flour", "bread", "gluten", "pasta", "barley", "rye", "crouton"]):
        allergens.append(ALLERGEN_WHEAT)
    if any(k in text_to_check for k in ["soy", "tofu", "edamame", "miso", "tempeh"]):
        allergens.append(ALLERGEN_SOY)
    if any(k in text_to_check for k in ["peanut", "peanuts"]):
        allergens.append(ALLERGEN_PEANUTS)
    if any(k in text_to_check for k in ["almond", "walnut", "cashew", "pecan", "pistachio", "hazelnut", "macadamia"]):
        allergens.append(ALLERGEN_TREE_NUTS)
    if any(k in text_to_check for k in ["fish", "salmon", "tuna", "cod", "trout", "anchovy", "halibut"]):
        allergens.append(ALLERGEN_FISH)
    if any(k in text_to_check for k in ["shrimp", "prawn", "crab", "lobster", "clam", "mussel", "oyster", "scallop"]):
        allergens.append(ALLERGEN_SHELLFISH)

    is_meat_or_fish = any(k in text_to_check for k in [
        "chicken", "beef", "pork", "lamb", "turkey", "bacon", "sausage", "meat", "fish", "salmon", "tuna", "cod", "shrimp", "prawn", "seafood"
    ])
    is_dairy_or_egg = (ALLERGEN_MILK in allergens) or (ALLERGEN_EGGS in allergens)

    is_vegan = not is_meat_or_fish and not is_dairy_or_egg and "honey" not in text_to_check
    is_vegetarian = not is_meat_or_fish
    is_dairy_free = ALLERGEN_MILK not in allergens
    is_gluten_free = ALLERGEN_WHEAT not in allergens

    return {
        "calories": round(calories),
        "protein": round(protein, 1),
        "carbs": round(carbs, 1),
        "fat": round(fat, 1),
        "fiber": round(fiber, 1),
        "sugar": round(sugar, 1),
        "sat_fat": round(sat_fat, 1),
        "sodium": round(sodium, 1),
        "allergens": sorted(set(allergens)),
        "is_vegan": is_vegan,
        "is_vegetarian": is_vegetarian,
        "is_dairy_free": is_dairy_free,
        "is_gluten_free": is_gluten_free,
    }


def _find_food_data(ingredient_name: str) -> dict[str, Any] | None:
    """Find food composition data with exact, singular, keyword matching, and USDA API fallback."""
    clean = ingredient_name.strip().lower()
    if clean in FOOD_COMPOSITION_PER_100G:
        return FOOD_COMPOSITION_PER_100G[clean]

    # Try singular (strip trailing s or es)
    singular = re.sub(r"(?:es|s)$", "", clean)
    if singular in FOOD_COMPOSITION_PER_100G:
        return FOOD_COMPOSITION_PER_100G[singular]

    # Match key in clean (e.g. "peanut butter" before "butter")
    for key in sorted(FOOD_COMPOSITION_PER_100G.keys(), key=len, reverse=True):
        if re.search(r"\b" + re.escape(key) + r"\b", clean) or (len(key) >= 4 and key in clean):
            return FOOD_COMPOSITION_PER_100G[key]

    # Match clean in key if clean is substantial (>= 4 chars) and is a word
    if len(clean) >= 4:
        for key in sorted(FOOD_COMPOSITION_PER_100G.keys(), key=len):
            if re.search(r"\b" + re.escape(clean) + r"\b", key):
                return FOOD_COMPOSITION_PER_100G[key]

    # Live USDA FoodData Central fallback for any new/unmapped ingredient
    usda_data = fetch_usda_nutrition(clean)
    if usda_data is not None:
        FOOD_COMPOSITION_PER_100G[clean] = usda_data
        _save_cached_food(clean, usda_data)
        return usda_data

    return None


def calculate_recipe_nutrition(
    recipe: Recipe, servings: float = 1.0
) -> dict[str, Any]:
    """
    Calculate deterministic nutritional profile for a recipe, scaled by serving count.

    Returns:
        dict with calories, macros, micros, dietary_tags, allergens, confidence, and scaling info.
    """
    if servings <= 0:
        servings = 1.0

    total_cal = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    total_fiber = 0.0
    total_sugar = 0.0
    total_sat_fat = 0.0
    total_sodium = 0.0

    allergens_found: set[str] = set()
    is_vegan = True
    is_vegetarian = True
    is_dairy_free = True
    is_gluten_free = True

    matched_count = 0
    unmatched_names: list[str] = []

    ingredients_count = len(recipe.ingredients)

    for assoc in recipe.ingredients:
        if not assoc.ingredient:
            continue

        raw_name = assoc.ingredient.name
        food_data = _find_food_data(raw_name)

        if food_data is not None:
            matched_count += 1
            grams = _get_grams_for_ingredient(raw_name, float(assoc.quantity), assoc.unit)
            multiplier = grams / 100.0

            total_cal += food_data["calories"] * multiplier
            total_protein += food_data["protein"] * multiplier
            total_carbs += food_data["carbs"] * multiplier
            total_fat += food_data["fat"] * multiplier
            total_fiber += food_data["fiber"] * multiplier
            total_sugar += food_data["sugar"] * multiplier
            total_sat_fat += food_data["sat_fat"] * multiplier
            total_sodium += food_data["sodium"] * multiplier

            for a in food_data["allergens"]:
                allergens_found.add(a)

            if not food_data.get("is_vegan", False):
                is_vegan = False
            if not food_data.get("is_vegetarian", False):
                is_vegetarian = False
            if not food_data.get("is_dairy_free", False):
                is_dairy_free = False
            if not food_data.get("is_gluten_free", False):
                is_gluten_free = False
        else:
            unmatched_names.append(raw_name)

    confidence = round(matched_count / max(ingredients_count, 1), 2)

    # Base recipe is for 1 person (1 serving).
    per_serving_cal = round(total_cal)
    per_serving_protein = round(total_protein, 1)
    per_serving_carbs = round(total_carbs, 1)
    per_serving_fat = round(total_fat, 1)
    per_serving_fiber = round(total_fiber, 1)
    per_serving_sugar = round(total_sugar, 1)
    per_serving_sat_fat = round(total_sat_fat, 1)
    per_serving_sodium = round(total_sodium, 1)

    # Scaled total = per_serving * servings
    scaled_cal = round(per_serving_cal * servings)
    scaled_protein = round(per_serving_protein * servings, 1)
    scaled_carbs = round(per_serving_carbs * servings, 1)
    scaled_fat = round(per_serving_fat * servings, 1)
    scaled_fiber = round(per_serving_fiber * servings, 1)
    scaled_sugar = round(per_serving_sugar * servings, 1)
    scaled_sat_fat = round(per_serving_sat_fat * servings, 1)
    scaled_sodium = round(per_serving_sodium * servings, 1)

    # Derive Dietary Labels
    dietary_tags: list[str] = []
    if is_vegan:
        dietary_tags.append("Vegan")
    elif is_vegetarian:
        dietary_tags.append("Vegetarian")

    if is_dairy_free:
        dietary_tags.append("Dairy-Free")

    if is_gluten_free:
        dietary_tags.append("Gluten-Free")

    if per_serving_protein >= 25.0:
        dietary_tags.append("High-Protein")

    if per_serving_carbs <= 20.0 and per_serving_cal > 0:
        dietary_tags.append("Low-Carb")

    return {
        "servings": servings,
        "per_serving": {
            "calories": per_serving_cal,
            "protein": per_serving_protein,
            "carbohydrates": per_serving_carbs,
            "fat": per_serving_fat,
            "fiber": per_serving_fiber,
            "sugar": per_serving_sugar,
            "saturated_fat": per_serving_sat_fat,
            "sodium": per_serving_sodium,
        },
        "total": {
            "calories": scaled_cal,
            "protein": scaled_protein,
            "carbohydrates": scaled_carbs,
            "fat": scaled_fat,
            "fiber": scaled_fiber,
            "sugar": scaled_sugar,
            "saturated_fat": scaled_sat_fat,
            "sodium": scaled_sodium,
        },
        "dietary_tags": dietary_tags,
        "allergens": sorted(allergens_found),
        "confidence_score": confidence,
        "unmatched_ingredients": unmatched_names,
        "is_estimate": len(unmatched_names) > 0,
    }

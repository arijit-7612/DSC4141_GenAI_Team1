from __future__ import annotations

from pydantic import BaseModel


class MacroNutrients(BaseModel):
    calories: int
    protein: float
    carbohydrates: float
    fat: float
    fiber: float
    sugar: float
    saturated_fat: float
    sodium: float


class RecipeNutritionRead(BaseModel):
    servings: int
    per_serving: MacroNutrients
    total: MacroNutrients
    dietary_tags: list[str]
    allergens: list[str]
    confidence_score: float
    unmatched_ingredients: list[str]
    is_estimate: bool

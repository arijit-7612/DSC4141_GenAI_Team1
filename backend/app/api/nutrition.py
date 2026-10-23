from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.nutrition import RecipeNutritionRead
from app.services import recipe_service
from app.services.nutrition_service import calculate_recipe_nutrition

router = APIRouter(prefix="/api/recipes", tags=["nutrition"])


@router.get("/{recipe_id}/nutrition", response_model=RecipeNutritionRead)
def get_recipe_nutrition(
    recipe_id: int,
    servings: int = Query(1, ge=1, le=50, description="Number of servings to scale for"),
    db: Session = Depends(get_db),
) -> dict:
    recipe = recipe_service._get_recipe_or_404(db, recipe_id)
    return calculate_recipe_nutrition(recipe, servings=servings)

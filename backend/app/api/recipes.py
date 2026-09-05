from collections.abc import Sequence

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.recipe import RecipeCreate, RecipeRead, RecipeUpdate
from app.services import recipe_service


router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def create_recipe(payload: RecipeCreate, db: Session = Depends(get_db)) -> RecipeRead:
    return recipe_service.create_recipe(db, payload)


@router.get("", response_model=list[RecipeRead])
def list_recipes(db: Session = Depends(get_db)) -> Sequence[RecipeRead]:
    return recipe_service.list_recipes(db)


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)) -> RecipeRead:
    return recipe_service.get_recipe(db, recipe_id)


@router.put("/{recipe_id}", response_model=RecipeRead)
def update_recipe(
    recipe_id: int, payload: RecipeUpdate, db: Session = Depends(get_db)
) -> RecipeRead:
    return recipe_service.update_recipe(db, recipe_id, payload)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)) -> Response:
    recipe_service.delete_recipe(db, recipe_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

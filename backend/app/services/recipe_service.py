"""Recipe persistence and ingredient association logic."""

from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Ingredient, Recipe, RecipeIngredient
from app.schemas.recipe import (
    RecipeCreate,
    RecipeIngredientRead,
    RecipeRead,
    RecipeUpdate,
    normalize_name,
)


def _recipe_query():
    return select(Recipe).options(
        selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient)
    )


def _get_recipe_or_404(db: Session, recipe_id: int) -> Recipe:
    recipe = db.scalar(_recipe_query().where(Recipe.id == recipe_id))
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe


def _get_or_create_ingredient(db: Session, name: str) -> Ingredient:
    ingredient = db.scalar(
        select(Ingredient).where(func.lower(Ingredient.name) == name.casefold())
    )
    if ingredient is None:
        ingredient = Ingredient(name=name)
        db.add(ingredient)
        db.flush()
    else:
        ingredient.name = normalize_name(ingredient.name)
    return ingredient


def _replace_ingredients(
    db: Session, recipe: Recipe, ingredients: list
) -> None:
    recipe.ingredients.clear()
    db.flush()
    for item in ingredients:
        recipe.ingredients.append(
            RecipeIngredient(
                ingredient=_get_or_create_ingredient(db, item.name),
                quantity=item.quantity,
                unit=item.unit,
            )
        )


def _serialize(recipe: Recipe) -> RecipeRead:
    return RecipeRead(
        id=recipe.id,
        name=normalize_name(recipe.name),
        ingredients=[
            RecipeIngredientRead(
                id=association.ingredient.id,
                name=normalize_name(association.ingredient.name),
                quantity=float(association.quantity),
                unit=association.unit,
            )
            for association in recipe.ingredients
        ],
    )


def create_recipe(db: Session, payload: RecipeCreate) -> RecipeRead:
    recipe = Recipe(name=payload.name)
    db.add(recipe)
    db.flush()
    _replace_ingredients(db, recipe, payload.ingredients)
    db.commit()
    return _serialize(_get_recipe_or_404(db, recipe.id))


def list_recipes(db: Session) -> Sequence[RecipeRead]:
    recipes = db.scalars(_recipe_query().order_by(Recipe.name)).all()
    return [_serialize(recipe) for recipe in recipes]


def get_recipe(db: Session, recipe_id: int) -> RecipeRead:
    return _serialize(_get_recipe_or_404(db, recipe_id))


def update_recipe(db: Session, recipe_id: int, payload: RecipeUpdate) -> RecipeRead:
    recipe = _get_recipe_or_404(db, recipe_id)
    recipe.name = payload.name
    _replace_ingredients(db, recipe, payload.ingredients)
    db.commit()
    return _serialize(_get_recipe_or_404(db, recipe_id))


def delete_recipe(db: Session, recipe_id: int) -> None:
    recipe = _get_recipe_or_404(db, recipe_id)
    db.delete(recipe)
    db.commit()

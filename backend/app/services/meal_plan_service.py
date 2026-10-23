"""Meal plan slot persistence and retrieval logic."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import MealPlanItem, Recipe
from app.schemas.meal_plan import MealPlanSlotInput, MealPlanSlotRead

DAY_ORDER = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6,
    "Sunday": 7,
}

MEAL_ORDER = {
    "Breakfast": 1,
    "Lunch": 2,
    "Dinner": 3,
}


def _meal_plan_query():
    return select(MealPlanItem).options(selectinload(MealPlanItem.recipe))


def list_meal_plan_items(db: Session) -> list[MealPlanSlotRead]:
    items = db.scalars(_meal_plan_query()).all()
    # Sort by day of week then meal of day
    sorted_items = sorted(
        items,
        key=lambda item: (
            DAY_ORDER.get(item.day, 99),
            MEAL_ORDER.get(item.meal, 99),
        ),
    )
    return [
        MealPlanSlotRead(
            id=item.id,
            day=item.day,
            meal=item.meal,
            recipe_id=item.recipe_id,
            recipe_name=item.recipe.name if item.recipe else "Unknown Recipe",
        )
        for item in sorted_items
    ]


def set_meal_plan_slot(db: Session, payload: MealPlanSlotInput) -> MealPlanSlotRead:
    recipe = db.scalar(select(Recipe).where(Recipe.id == payload.recipe_id))
    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {payload.recipe_id} not found",
        )

    existing = db.scalar(
        select(MealPlanItem).where(
            MealPlanItem.day == payload.day,
            MealPlanItem.meal == payload.meal,
        )
    )

    if existing is not None:
        existing.recipe_id = payload.recipe_id
        db.commit()
        db.refresh(existing)
        item = existing
    else:
        item = MealPlanItem(
            day=payload.day,
            meal=payload.meal,
            recipe_id=payload.recipe_id,
        )
        db.add(item)
        db.commit()
        db.refresh(item)

    return MealPlanSlotRead(
        id=item.id,
        day=item.day,
        meal=item.meal,
        recipe_id=item.recipe_id,
        recipe_name=recipe.name,
    )


def remove_meal_plan_slot(db: Session, day: str, meal: str) -> None:
    item = db.scalar(
        select(MealPlanItem).where(
            MealPlanItem.day == day,
            MealPlanItem.meal == meal,
        )
    )
    if item is not None:
        db.delete(item)
        db.commit()


def clear_meal_plan(db: Session) -> None:
    items = db.scalars(select(MealPlanItem)).all()
    for item in items:
        db.delete(item)
    db.commit()

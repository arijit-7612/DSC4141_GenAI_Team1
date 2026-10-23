from collections.abc import Sequence

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.meal_plan import MealPlanSlotInput, MealPlanSlotRead
from app.services import meal_plan_service

router = APIRouter(prefix="/api/meal-plan", tags=["meal-plan"])


@router.get("", response_model=list[MealPlanSlotRead])
def list_meal_plan(db: Session = Depends(get_db)) -> Sequence[MealPlanSlotRead]:
    return meal_plan_service.list_meal_plan_items(db)


@router.post("", response_model=MealPlanSlotRead, status_code=status.HTTP_200_OK)
def set_meal_plan_slot(
    payload: MealPlanSlotInput, db: Session = Depends(get_db)
) -> MealPlanSlotRead:
    return meal_plan_service.set_meal_plan_slot(db, payload)


@router.delete("/{day}/{meal}", status_code=status.HTTP_204_NO_CONTENT)
def remove_meal_plan_slot(
    day: str, meal: str, db: Session = Depends(get_db)
) -> Response:
    meal_plan_service.remove_meal_plan_slot(db, day, meal)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_meal_plan(db: Session = Depends(get_db)) -> Response:
    meal_plan_service.clear_meal_plan(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

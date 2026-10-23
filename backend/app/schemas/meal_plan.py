from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DayType = Literal[
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

MealType = Literal["Breakfast", "Lunch", "Dinner"]


class MealPlanSlotInput(BaseModel):
    day: DayType
    meal: MealType
    recipe_id: int = Field(gt=0)


class MealPlanSlotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    day: DayType
    meal: MealType
    recipe_id: int
    recipe_name: str

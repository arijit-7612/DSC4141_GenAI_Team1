from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.recipe import Recipe


class MealPlanItem(Base):
    __tablename__ = "meal_plan_items"
    __table_args__ = (UniqueConstraint("day", "meal", name="uq_meal_plan_day_meal"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    day: Mapped[str] = mapped_column(String(20), nullable=False)
    meal: Mapped[str] = mapped_column(String(20), nullable=False)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False
    )

    recipe: Mapped[Recipe] = relationship()

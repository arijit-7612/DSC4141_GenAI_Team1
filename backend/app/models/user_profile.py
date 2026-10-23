from __future__ import annotations

import json

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), default="default_user", unique=True)
    # Stored as JSON strings
    _dietary_preferences: Mapped[str] = mapped_column("dietary_preferences", Text, default="[]")
    _allergies: Mapped[str] = mapped_column("allergies", Text, default="[]")

    @property
    def dietary_preferences(self) -> list[str]:
        try:
            return json.loads(self._dietary_preferences)
        except Exception:
            return []

    @dietary_preferences.setter
    def dietary_preferences(self, value: list[str]) -> None:
        self._dietary_preferences = json.dumps(value)

    @property
    def allergies(self) -> list[str]:
        try:
            return json.loads(self._allergies)
        except Exception:
            return []

    @allergies.setter
    def allergies(self, value: list[str]) -> None:
        self._allergies = json.dumps(value)

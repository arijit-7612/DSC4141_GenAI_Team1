from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UserProfileBase(BaseModel):
    dietary_preferences: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileRead(UserProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str

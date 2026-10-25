import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def email(value: str) -> str:
    value = value.strip().lower()
    if not EMAIL.fullmatch(value):
        raise ValueError("must be a valid email address")
    return value


class RegisterRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        return email(value)


class LoginRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        return email(value)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead

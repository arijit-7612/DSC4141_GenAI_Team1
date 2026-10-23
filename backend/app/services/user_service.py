from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileUpdate


def get_user_profile(db: Session, username: str = "default_user") -> UserProfile:
    profile = db.scalar(select(UserProfile).where(UserProfile.username == username))
    if profile is None:
        profile = UserProfile(username=username)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def update_user_profile(
    db: Session, payload: UserProfileUpdate, username: str = "default_user"
) -> UserProfile:
    profile = get_user_profile(db, username=username)
    profile.dietary_preferences = payload.dietary_preferences
    profile.allergies = payload.allergies
    db.commit()
    db.refresh(profile)
    return profile

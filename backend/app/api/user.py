from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user_profile import UserProfileRead, UserProfileUpdate
from app.services import user_service

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=UserProfileRead)
def get_profile(db: Session = Depends(get_db)) -> UserProfileRead:
    return user_service.get_user_profile(db)


@router.put("", response_model=UserProfileRead)
def update_profile(
    payload: UserProfileUpdate, db: Session = Depends(get_db)
) -> UserProfileRead:
    return user_service.update_user_profile(db, payload)

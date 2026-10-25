from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()


def response(user: User) -> TokenResponse:
    return TokenResponse(access_token=auth_service.create_token(user), user=user)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return response(auth_service.register(db, payload.email, payload.password))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return response(auth_service.authenticate(db, payload.email, payload.password))


@router.get("/me", response_model=UserRead)
def me(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    return auth_service.current_user(db, credentials.credentials)

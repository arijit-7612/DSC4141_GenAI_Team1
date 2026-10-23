from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.grocery_list import GroceryListResponse
from app.services import grocery_service

router = APIRouter(prefix="/api/grocery-list", tags=["grocery-list"])


@router.get("", response_model=GroceryListResponse)
def get_grocery_list(db: Session = Depends(get_db)) -> GroceryListResponse:
    return grocery_service.generate_grocery_list(db)

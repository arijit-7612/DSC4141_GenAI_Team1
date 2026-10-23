from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.grocery_list import router as grocery_list_router
from app.api.meal_plan import router as meal_plan_router
from app.api.nutrition import router as nutrition_router
from app.api.recipes import router as recipes_router
from app.api.user import router as user_router
from app.database import Base, SessionLocal, engine
from app.services.seed_data import seed_recipes_if_empty


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_recipes_if_empty(db)
    yield


app = FastAPI(title="AI Meal Planner & Grocery Assistant", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(recipes_router)
app.include_router(nutrition_router)
app.include_router(meal_plan_router)
app.include_router(grocery_list_router)
app.include_router(user_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

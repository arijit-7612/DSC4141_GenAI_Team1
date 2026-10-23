from pydantic import BaseModel, ConfigDict


class GroceryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    quantity: float
    unit: str
    category: str = "Other"
    show_quantity: bool = True
    display_quantity: str = ""
    recipes: list[str] = []


class GroceryCategoryGroup(BaseModel):
    category: str
    items: list[GroceryItem]


class GroceryListResponse(BaseModel):
    items: list[GroceryItem]
    categories: list[GroceryCategoryGroup]
    total_items: int
    total_recipes: int
    planned_meals_count: int

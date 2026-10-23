"""Grocery list generation, categorization, and ingredient aggregation logic."""

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import MealPlanItem, Recipe, RecipeIngredient
from app.schemas.grocery_list import (
    GroceryCategoryGroup,
    GroceryItem,
    GroceryListResponse,
)
from app.schemas.recipe import normalize_name
from app.services.ingredient_classifier import classify_ingredient

CATEGORY_ORDER = [
    "Produce",
    "Meat & Seafood",
    "Dairy & Eggs",
    "Bakery & Grains",
    "Canned & Packaged",
    "Spices & Seasonings",
    "Other",
]


def generate_grocery_list(db: Session) -> GroceryListResponse:
    """Aggregate and categorize ingredients across all planned meals in the weekly planner."""
    query = select(MealPlanItem).options(
        selectinload(MealPlanItem.recipe)
        .selectinload(Recipe.ingredients)
        .selectinload(RecipeIngredient.ingredient)
    )
    meal_slots = db.scalars(query).all()

    if not meal_slots:
        return GroceryListResponse(
            items=[],
            categories=[],
            total_items=0,
            total_recipes=0,
            planned_meals_count=0,
        )

    # Key: (normalized_name_lower, unit_lower)
    aggregated: dict[tuple[str, str], dict] = defaultdict(
        lambda: {"name": "", "unit": "", "quantity": 0.0, "recipes": set()}
    )

    planned_recipe_ids: set[int] = set()

    for slot in meal_slots:
        recipe = slot.recipe
        if recipe is None:
            continue

        planned_recipe_ids.add(recipe.id)

        for assoc in recipe.ingredients:
            if assoc.ingredient is None:
                continue

            raw_name = assoc.ingredient.name
            clean_name = normalize_name(raw_name)
            unit = assoc.unit.strip()
            quantity = float(assoc.quantity)

            key = (clean_name.casefold(), unit.casefold())
            entry = aggregated[key]
            entry["name"] = clean_name
            entry["unit"] = unit
            entry["quantity"] += quantity
            entry["recipes"].add(recipe.name)

    # Build classified items
    items: list[GroceryItem] = []
    category_buckets: dict[str, list[GroceryItem]] = defaultdict(list)

    for (_, _), data in sorted(aggregated.items(), key=lambda x: x[1]["name"].casefold()):
        qty = round(data["quantity"], 2)
        if qty.is_integer():
            qty = float(int(qty))

        category, show_quantity = classify_ingredient(data["name"], data["unit"])

        if show_quantity:
            display_quantity = f"{int(qty) if qty.is_integer() else qty} {data['unit']}"
        else:
            display_quantity = "Pantry staple"

        item = GroceryItem(
            name=data["name"],
            quantity=qty,
            unit=data["unit"],
            category=category,
            show_quantity=show_quantity,
            display_quantity=display_quantity,
            recipes=sorted(data["recipes"]),
        )
        items.append(item)
        category_buckets[category].append(item)

    # Build ordered category groups
    categories: list[GroceryCategoryGroup] = []
    for cat_name in CATEGORY_ORDER:
        if cat_name in category_buckets and category_buckets[cat_name]:
            categories.append(
                GroceryCategoryGroup(
                    category=cat_name,
                    items=category_buckets[cat_name],
                )
            )

    # Include any remaining unexpected categories
    for cat_name, cat_items in category_buckets.items():
        if cat_name not in CATEGORY_ORDER and cat_items:
            categories.append(
                GroceryCategoryGroup(
                    category=cat_name,
                    items=cat_items,
                )
            )

    return GroceryListResponse(
        items=items,
        categories=categories,
        total_items=len(items),
        total_recipes=len(planned_recipe_ids),
        planned_meals_count=len(meal_slots),
    )

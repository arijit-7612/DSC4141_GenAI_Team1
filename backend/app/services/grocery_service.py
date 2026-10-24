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

# Portion / serving units that should NEVER be shown as raw grocery store counts
PORTION_UNITS = {"slice", "slices", "tbsp", "tsp", "clove", "cloves", "pinch", "dash"}

# Items where shoppers buy the item, not small recipe increments
STAPLE_KEYWORDS = (
    "bread",
    "toast",
    "bun",
    "bagel",
    "tortilla",
    "wrap",
    "pita",
    "butter",
    "margarine",
    "ghee",
    "oil",
    "vinegar",
    "sauce",
    "dressing",
    "spread",
    "mayo",
    "mustard",
    "ketchup",
    "jam",
    "jelly",
    "honey",
    "syrup",
    "sugar",
    "salt",
    "pepper",
    "powder",
    "masala",
    "spice",
    "herb",
    "seasoning",
    "extract",
    "paste",
    "garlic",
    "clove",
)


def _canonical_name(name: str) -> str:
    cleaned = normalize_name(name)
    lower = cleaned.lower()
    # Canonicalize common plurals so "Tomatoes" and "Tomato" or "Eggs" and "Egg" merge
    if lower.endswith("es") and lower[:-2] in ["tomato", "potato"]:
        return normalize_name(lower[:-2])
    if lower.endswith("s") and not lower.endswith("ss") and lower[:-1] in [
        "egg",
        "carrot",
        "onion",
        "banana",
        "apple",
        "lemon",
        "lime",
        "mushroom",
        "cucumber",
    ]:
        return normalize_name(lower[:-1])
    return cleaned


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

    # Key: canonical ingredient name (lower) -> dictionary of accumulated data
    # Guarantees that NO ingredient is EVER duplicated on the grocery list!
    aggregated: dict[str, dict] = defaultdict(
        lambda: {"name": "", "entries": [], "recipes": set()}
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
            clean_name = _canonical_name(raw_name)
            unit = assoc.unit.strip()
            quantity = float(assoc.quantity)

            key = clean_name.casefold()
            entry = aggregated[key]
            if not entry["name"]:
                entry["name"] = clean_name
            entry["entries"].append((quantity, unit))
            entry["recipes"].add(recipe.name)

    items: list[GroceryItem] = []
    category_buckets: dict[str, list[GroceryItem]] = defaultdict(list)

    for _, data in sorted(aggregated.items(), key=lambda x: x[1]["name"].casefold()):
        name = data["name"]
        entries: list[tuple[float, str]] = data["entries"]
        recipes = sorted(data["recipes"])
        primary_unit = entries[0][1]

        # Determine category and whether quantity should be shown
        category, show_quantity = classify_ingredient(name, primary_unit)

        # Enforce staple / portion rules:
        # If any recipe uses slice/tbsp/tsp/clove, or item is bread/butter/cheese/oil/spice/seasoning
        # do NOT show raw slice / spoon quantities on the grocery list!
        lower_name = name.lower()
        has_portion_unit = any(u.lower() in PORTION_UNITS for _, u in entries)
        is_staple_name = any(k in lower_name for k in STAPLE_KEYWORDS)

        if has_portion_unit or is_staple_name:
            show_quantity = False

        if show_quantity:
            # Check unit compatibility to combine measurements
            distinct_units = {u.lower() for _, u in entries}

            if len(distinct_units) == 1:
                # Same unit everywhere: sum measurements directly
                total_qty = sum(q for q, _ in entries)
                final_qty = round(total_qty, 2)
                if final_qty.is_integer():
                    final_qty = float(int(final_qty))
                final_unit = entries[0][1]
                display_quantity = (
                    f"{int(final_qty) if final_qty.is_integer() else final_qty} {final_unit}"
                )
            elif distinct_units.issubset({"g", "kg"}):
                # Convert to grams and sum
                total_g = sum(
                    q * 1000.0 if u.lower() == "kg" else q for q, u in entries
                )
                if total_g >= 1000.0:
                    final_qty = round(total_g / 1000.0, 2)
                    final_unit = "kg"
                else:
                    final_qty = round(total_g, 2)
                    final_unit = "g"
                if final_qty.is_integer():
                    final_qty = float(int(final_qty))
                display_quantity = (
                    f"{int(final_qty) if final_qty.is_integer() else final_qty} {final_unit}"
                )
            elif distinct_units.issubset({"ml", "l"}):
                # Convert to ml and sum
                total_ml = sum(
                    q * 1000.0 if u.lower() == "l" else q for q, u in entries
                )
                if total_ml >= 1000.0:
                    final_qty = round(total_ml / 1000.0, 2)
                    final_unit = "L"
                else:
                    final_qty = round(total_ml, 2)
                    final_unit = "ml"
                if final_qty.is_integer():
                    final_qty = float(int(final_qty))
                display_quantity = (
                    f"{int(final_qty) if final_qty.is_integer() else final_qty} {final_unit}"
                )
            else:
                # Incompatible measurements across recipes (e.g. piece vs grams)
                # As requested: "else just write once"
                show_quantity = False
                final_qty = sum(q for q, _ in entries)
                final_unit = primary_unit
                display_quantity = "Pantry staple"
        else:
            # Staples, spices, breads, butters, cheeses, oils
            total_qty = sum(q for q, _ in entries)
            final_qty = round(total_qty, 2)
            if final_qty.is_integer():
                final_qty = float(int(final_qty))
            final_unit = primary_unit
            display_quantity = "Pantry staple"

        item = GroceryItem(
            name=name,
            quantity=final_qty,
            unit=final_unit,
            category=category,
            show_quantity=show_quantity,
            display_quantity=display_quantity,
            recipes=recipes,
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

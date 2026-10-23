"""Ingredient categorization and quantity visibility classification service.

Hybrid architecture:
1. Local culinary knowledge base for high-frequency ingredients.
2. Optional GenAI integration (OpenAI / LLM) for new / unfamiliar ingredients.
3. Intelligent heuristic rule-engine fallback.
"""

import json
import os
import re

# Standard supermarket categories
CAT_PRODUCE = "Produce"
CAT_MEAT = "Meat & Seafood"
CAT_DAIRY = "Dairy & Eggs"
CAT_GRAINS = "Bakery & Grains"
CAT_CANNED = "Canned & Packaged"
CAT_SPICES = "Spices & Seasonings"
CAT_OTHER = "Other"

# Common ingredients lookup dictionary: name -> (category, show_quantity)
# Spices, seasonings, garlic, salt, pepper, oils, sugar -> show_quantity = False
KNOWN_INGREDIENTS: dict[str, tuple[str, bool]] = {
    # Spices, Seasonings, Aromatics & Pantry Staples (hide micro-quantities)
    "salt": (CAT_SPICES, False),
    "black pepper": (CAT_SPICES, False),
    "white pepper": (CAT_SPICES, False),
    "red chili flakes": (CAT_SPICES, False),
    "red chili powder": (CAT_SPICES, False),
    "chili powder": (CAT_SPICES, False),
    "garlic": (CAT_SPICES, False),
    "garlic powder": (CAT_SPICES, False),
    "onion powder": (CAT_SPICES, False),
    "turmeric": (CAT_SPICES, False),
    "turmeric powder": (CAT_SPICES, False),
    "cumin": (CAT_SPICES, False),
    "cumin seeds": (CAT_SPICES, False),
    "cumin powder": (CAT_SPICES, False),
    "garam masala": (CAT_SPICES, False),
    "cinnamon": (CAT_SPICES, False),
    "cinnamon powder": (CAT_SPICES, False),
    "dried oregano": (CAT_SPICES, False),
    "oregano": (CAT_SPICES, False),
    "smoked paprika": (CAT_SPICES, False),
    "paprika": (CAT_SPICES, False),
    "white sugar": (CAT_SPICES, False),
    "brown sugar": (CAT_SPICES, False),
    "sugar": (CAT_SPICES, False),
    "olive oil": (CAT_SPICES, False),
    "extra virgin olive oil": (CAT_SPICES, False),
    "sesame oil": (CAT_SPICES, False),
    "vegetable oil": (CAT_SPICES, False),
    "canola oil": (CAT_SPICES, False),
    "sunflower oil": (CAT_SPICES, False),
    "soy sauce": (CAT_SPICES, False),
    "ginger garlic paste": (CAT_SPICES, False),
    "baking powder": (CAT_SPICES, False),
    "baking soda": (CAT_SPICES, False),
    "vanilla extract": (CAT_SPICES, False),
    "chia seeds": (CAT_SPICES, False),
    "sesame seeds": (CAT_SPICES, False),
    "mustard seeds": (CAT_SPICES, False),
    "coriander powder": (CAT_SPICES, False),
    "cardamom": (CAT_SPICES, False),
    "cloves": (CAT_SPICES, False),
    "nutmeg": (CAT_SPICES, False),
    "vinegar": (CAT_SPICES, False),
    "apple cider vinegar": (CAT_SPICES, False),
    "balsamic vinegar": (CAT_SPICES, False),
    "honey": (CAT_SPICES, False),
    "maple syrup": (CAT_SPICES, False),
    # Fresh Produce (show quantities)
    "tomato": (CAT_PRODUCE, True),
    "cucumber": (CAT_PRODUCE, True),
    "onion": (CAT_PRODUCE, True),
    "red onion": (CAT_PRODUCE, True),
    "broccoli": (CAT_PRODUCE, True),
    "carrot": (CAT_PRODUCE, True),
    "carrots": (CAT_PRODUCE, True),
    "bell pepper": (CAT_PRODUCE, True),
    "zucchini": (CAT_PRODUCE, True),
    "fresh spinach": (CAT_PRODUCE, True),
    "spinach": (CAT_PRODUCE, True),
    "mushroom": (CAT_PRODUCE, True),
    "mushrooms": (CAT_PRODUCE, True),
    "asparagus": (CAT_PRODUCE, True),
    "avocado": (CAT_PRODUCE, True),
    "lemon": (CAT_PRODUCE, True),
    "lime": (CAT_PRODUCE, True),
    "banana": (CAT_PRODUCE, True),
    "mixed berries": (CAT_PRODUCE, True),
    "berries": (CAT_PRODUCE, True),
    "fresh basil": (CAT_PRODUCE, True),
    "basil": (CAT_PRODUCE, True),
    "romaine lettuce": (CAT_PRODUCE, True),
    "lettuce": (CAT_PRODUCE, True),
    "green onion": (CAT_PRODUCE, True),
    "spring onion": (CAT_PRODUCE, True),
    "potato": (CAT_PRODUCE, True),
    "potatoes": (CAT_PRODUCE, True),
    "sweet potato": (CAT_PRODUCE, True),
    "ginger": (CAT_PRODUCE, True),
    "cilantro": (CAT_PRODUCE, True),
    "parsley": (CAT_PRODUCE, True),
    # Meat & Seafood (show quantities)
    "chicken breast": (CAT_MEAT, True),
    "chicken": (CAT_MEAT, True),
    "chicken thigh": (CAT_MEAT, True),
    "salmon fillet": (CAT_MEAT, True),
    "salmon": (CAT_MEAT, True),
    "shrimp": (CAT_MEAT, True),
    "ground beef": (CAT_MEAT, True),
    "beef": (CAT_MEAT, True),
    "pork": (CAT_MEAT, True),
    "tuna": (CAT_MEAT, True),
    "turkey": (CAT_MEAT, True),
    "bacon": (CAT_MEAT, True),
    # Dairy & Eggs (show quantities)
    "egg": (CAT_DAIRY, True),
    "eggs": (CAT_DAIRY, True),
    "milk": (CAT_DAIRY, True),
    "whole milk": (CAT_DAIRY, True),
    "greek yogurt": (CAT_DAIRY, True),
    "yogurt": (CAT_DAIRY, True),
    "butter": (CAT_DAIRY, True),
    "cheddar cheese": (CAT_DAIRY, True),
    "parmesan cheese": (CAT_DAIRY, True),
    "feta cheese": (CAT_DAIRY, True),
    "paneer": (CAT_DAIRY, True),
    "heavy cream": (CAT_DAIRY, True),
    "mozzarella": (CAT_DAIRY, True),
    # Bakery & Grains (show quantities)
    "penne pasta": (CAT_GRAINS, True),
    "pasta": (CAT_GRAINS, True),
    "spaghetti": (CAT_GRAINS, True),
    "basmati rice": (CAT_GRAINS, True),
    "rice": (CAT_GRAINS, True),
    "jasmine rice": (CAT_GRAINS, True),
    "sourdough bread": (CAT_GRAINS, True),
    "bread": (CAT_GRAINS, True),
    "tortilla wrap": (CAT_GRAINS, True),
    "tortilla": (CAT_GRAINS, True),
    "wrap": (CAT_GRAINS, True),
    "quinoa": (CAT_GRAINS, True),
    "rolled oats": (CAT_GRAINS, True),
    "oats": (CAT_GRAINS, True),
    "granola": (CAT_GRAINS, True),
    "all-purpose flour": (CAT_GRAINS, True),
    "flour": (CAT_GRAINS, True),
    "croutons": (CAT_GRAINS, True),
    "noodles": (CAT_GRAINS, True),
    # Canned & Packaged / Plant Proteins (show quantities)
    "chickpeas": (CAT_CANNED, True),
    "canned tomato": (CAT_CANNED, True),
    "canned tomatoes": (CAT_CANNED, True),
    "red lentils": (CAT_CANNED, True),
    "lentils": (CAT_CANNED, True),
    "firm tofu": (CAT_CANNED, True),
    "tofu": (CAT_CANNED, True),
    "black beans": (CAT_CANNED, True),
    "kidney beans": (CAT_CANNED, True),
}


AI_CACHE: dict[str, tuple[str, bool]] = {}


def _try_ai_classification(ingredient_name: str, unit: str = "") -> tuple[str, bool] | None:
    """Classify unfamiliar ingredient using Groq (or OpenAI) if API key is present."""
    cache_key = ingredient_name.strip().lower()
    if cache_key in AI_CACHE:
        return AI_CACHE[cache_key]

    # Ensure environment variables from .env are loaded
    try:
        from dotenv import load_dotenv
        load_dotenv()
        from pathlib import Path
        backend_env = Path(__file__).resolve().parent.parent.parent / ".env"
        if backend_env.exists():
            load_dotenv(backend_env)
    except Exception:
        pass

    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if groq_key:
        api_url = "https://api.groq.com/openai/v1/chat/completions"
        api_key = groq_key
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    elif openai_key:
        api_url = "https://api.openai.com/v1/chat/completions"
        api_key = openai_key
        model = "gpt-4o-mini"
    else:
        return None

    try:
        import urllib.request

        prompt = (
            f"You are an expert grocery aisle classifier. Classify the ingredient '{ingredient_name}'"
            + (f" (measured in '{unit}')" if unit else "")
            + ". Choose exactly one category from: 'Produce', 'Meat & Seafood', 'Dairy & Eggs', 'Bakery & Grains', 'Canned & Packaged', 'Spices & Seasonings', 'Other'. "
            "Also decide if shoppers need to see exact recipe quantities (true for meats, eggs, vegetables, dairy, grains; false for spices, salt, seasonings, cooking oils, garlic, sugar). "
            'Respond ONLY with valid JSON: {"category": "...", "show_quantity": true/false}'
        )

        req_data = json.dumps(
            {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "response_format": {"type": "json_object"},
            }
        ).encode("utf-8")

        req = urllib.request.Request(
            api_url,
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "MealPlannerApp/1.0",
            },
        )

        with urllib.request.urlopen(req, timeout=4.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            cat = parsed.get("category", CAT_OTHER)
            show_qty = bool(parsed.get("show_quantity", True))
            AI_CACHE[cache_key] = (cat, show_qty)
            return cat, show_qty
    except Exception:
        return None


def _heuristic_classification(name: str, unit: str) -> tuple[str, bool]:
    """Smart heuristic rule-engine fallback for ingredients not in knowledge base."""
    n = name.lower()
    u = unit.lower()

    # Rule 1: Units typically associated with micro-seasonings
    if u in ("tsp", "clove"):
        return CAT_SPICES, False

    # Rule 2: Keywords for spices, seasonings, condiments
    spice_keywords = (
        "salt",
        "pepper",
        "powder",
        "masala",
        "spice",
        "seed",
        "seeds",
        "flake",
        "flakes",
        "oil",
        "vinegar",
        "sugar",
        "extract",
        "sauce",
        "paste",
        "seasoning",
        "herb",
        "clove",
        "syrup",
        "cinnamon",
        "cumin",
        "oregano",
        "garlic",
    )
    if any(k in n for k in spice_keywords):
        return CAT_SPICES, False

    # Rule 3: Meat & Seafood
    meat_keywords = (
        "chicken",
        "beef",
        "pork",
        "salmon",
        "fish",
        "shrimp",
        "steak",
        "turkey",
        "meat",
        "tuna",
        "lamb",
        "bacon",
        "sausage",
    )
    if any(k in n for k in meat_keywords):
        return CAT_MEAT, True

    # Rule 4: Dairy & Eggs
    dairy_keywords = (
        "egg",
        "milk",
        "cheese",
        "yogurt",
        "butter",
        "cream",
        "paneer",
        "curd",
        "ghee",
    )
    if any(k in n for k in dairy_keywords):
        return CAT_DAIRY, True

    # Rule 5: Bakery & Grains
    grain_keywords = (
        "pasta",
        "rice",
        "bread",
        "oat",
        "flour",
        "quinoa",
        "tortilla",
        "wrap",
        "noodle",
        "cereal",
        "granola",
        "crouton",
    )
    if any(k in n for k in grain_keywords):
        return CAT_GRAINS, True

    # Rule 6: Canned & Packaged / Beans / Tofu
    canned_keywords = ("canned", "bean", "lentil", "tofu", "chickpea", "edamame", "tempeh")
    if any(k in n for k in canned_keywords):
        return CAT_CANNED, True

    # Rule 7: Produce
    produce_keywords = (
        "tomato",
        "onion",
        "pepper",
        "broccoli",
        "carrot",
        "spinach",
        "lettuce",
        "cucumber",
        "zucchini",
        "asparagus",
        "avocado",
        "lemon",
        "lime",
        "banana",
        "berry",
        "apple",
        "potato",
        "mushroom",
        "cilantro",
        "basil",
        "leaf",
        "leaves",
        "cabbage",
        "cauliflower",
    )
    if any(k in n for k in produce_keywords):
        return CAT_PRODUCE, True

    return CAT_OTHER, True


def classify_ingredient(name: str, unit: str = "") -> tuple[str, bool]:
    """
    Classify any ingredient into a standard supermarket category and determine
    whether exact recipe quantity should be shown on the grocery list.

    Returns:
        (category: str, show_quantity: bool)
    """
    clean_name = name.strip().lower()

    # 1. Exact or normalized dictionary lookup
    if clean_name in KNOWN_INGREDIENTS:
        return KNOWN_INGREDIENTS[clean_name]

    # Remove extra plural / whitespace
    singular_name = re.sub(r"s$", "", clean_name)
    if singular_name in KNOWN_INGREDIENTS:
        return KNOWN_INGREDIENTS[singular_name]

    # 2. Try GenAI classification if configured
    ai_result = _try_ai_classification(name, unit)
    if ai_result is not None:
        return ai_result

    # 3. Fast heuristic rule engine fallback
    return _heuristic_classification(name, unit)

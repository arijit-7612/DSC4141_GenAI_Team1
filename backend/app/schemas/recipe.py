from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


RecipeUnit = Literal[
    "g",
    "kg",
    "ml",
    "L",
    "tsp",
    "tbsp",
    "cup",
    "piece",
    "clove",
    "slice",
    "can",
    "packet",
    "bottle",
    "bunch",
]


def normalize_name(value: str) -> str:
    """Normalize names to title case with single spaces."""
    value = " ".join(value.split())
    return " ".join(word.capitalize() for word in value.split(" "))


class RecipeIngredientInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    quantity: float = Field(gt=0)
    unit: RecipeUnit

    @field_validator("name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = normalize_name(value)
        if not value:
            raise ValueError("must not be blank")
        return value


class RecipeBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    ingredients: list[RecipeIngredientInput] = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def strip_recipe_name(cls, value: str) -> str:
        value = normalize_name(value)
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("ingredients")
    @classmethod
    def reject_duplicate_ingredients(
        cls, ingredients: list[RecipeIngredientInput]
    ) -> list[RecipeIngredientInput]:
        normalized_names = [ingredient.name.casefold() for ingredient in ingredients]
        if len(normalized_names) != len(set(normalized_names)):
            raise ValueError("each ingredient may appear only once in a recipe")
        return ingredients


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(RecipeBase):
    pass


class RecipeIngredientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    quantity: float
    unit: str


class RecipeRead(BaseModel):
    id: int
    name: str
    ingredients: list[RecipeIngredientRead]

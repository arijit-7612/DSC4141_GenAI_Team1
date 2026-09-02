from pydantic import BaseModel, ConfigDict, Field, field_validator


class RecipeIngredientInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=50)

    @field_validator("name", "unit")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class RecipeBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    ingredients: list[RecipeIngredientInput] = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def strip_recipe_name(cls, value: str) -> str:
        value = value.strip()
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

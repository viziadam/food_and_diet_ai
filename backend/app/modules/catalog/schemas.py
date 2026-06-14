from pydantic import BaseModel, ConfigDict


class IngredientSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    quantity_grams: float
    display_quantity: str


class RecipeSummary(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    meal_type: str
    cuisine: str
    prep_minutes: int
    cook_minutes: int
    tags: list[str]

from datetime import date

from pydantic import BaseModel

from app.modules.planning.schemas import Cuisine, MealType


class MacroSummary(BaseModel):
    calories_kcal: int
    protein_g: float
    carbs_g: float
    fat_g: float


class PlannedIngredient(BaseModel):
    ingredient_id: int
    name: str
    quantity_grams: float
    display_quantity: str
    estimated_cost_huf: int
    package_size_grams: float
    package_price_huf: int
    price_store: str
    price_source: str
    price_checked_at: date | None
    seasonal: bool


class PlannedMeal(BaseModel):
    recipe_id: int
    name: str
    description: str
    meal_type: MealType
    cuisine: Cuisine
    servings: int
    prep_minutes: int
    cook_minutes: int
    nutrition_per_person: MacroSummary
    estimated_cost_huf: int
    purchase_cost_huf: int
    seasonal_ratio: float
    ingredients: list[PlannedIngredient]
    instructions: list[str]


class MealOptionGroup(BaseModel):
    meal_type: MealType
    recommended_recipe_id: int
    options: list[PlannedMeal]


class ShoppingListItem(BaseModel):
    ingredient_id: int
    name: str
    required_quantity_grams: float
    package_size_grams: float
    package_price_huf: int
    packages_to_buy: int
    purchase_quantity_grams: float
    proportional_cost_huf: int
    purchase_cost_huf: int
    leftover_after_plan_grams: float
    price_store: str
    price_source: str
    price_checked_at: date | None
    seasonal: bool


class PlanSummary(BaseModel):
    people_count: int
    calories_per_person: int
    calorie_target_per_person: int
    proportional_total_cost_huf: int
    full_purchase_total_cost_huf: int
    shopping_total_cost_huf: int
    estimated_total_cost_huf: int
    budget_huf: int
    budget_difference_huf: int
    protein_per_person_g: float
    carbs_per_person_g: float
    fat_per_person_g: float
    seasonal_ingredient_ratio: float


class MealPlanResponse(BaseModel):
    id: str
    summary: PlanSummary
    meals: list[PlannedMeal]
    meal_options: list[MealOptionGroup]
    shopping_list: list[ShoppingListItem]
    notices: list[str]

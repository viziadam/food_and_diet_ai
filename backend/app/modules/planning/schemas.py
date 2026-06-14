from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class Goal(StrEnum):
    WEIGHT_LOSS = "weight_loss"
    CONSCIOUS = "conscious"
    HIGH_PROTEIN = "high_protein"


class MealType(StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class Cuisine(StrEnum):
    HUNGARIAN = "hungarian"
    ITALIAN = "italian"
    MEDITERRANEAN = "mediterranean"
    MIXED = "mixed"


class DietaryPreference(StrEnum):
    VEGETARIAN = "vegetarian"
    LACTOSE_FREE = "lactose_free"
    GLUTEN_FREE = "gluten_free"


class CostCalculationMode(StrEnum):
    PROPORTIONAL = "proportional"
    ASSUME_EMPTY = "assume_empty"
    PANTRY_AWARE = "pantry_aware"


class PantryItemInput(BaseModel):
    ingredient_id: int = Field(gt=0)
    quantity_grams: float = Field(gt=0, le=100_000)


class MealPlanRequest(BaseModel):
    people_count: int = Field(default=1, ge=1, le=10)
    calorie_target_per_person: int = Field(
        default=1900,
        ge=1000,
        le=5000,
    )
    daily_budget_huf: int = Field(
        default=5000,
        ge=1000,
        le=100000,
    )

    goal: Goal = Goal.CONSCIOUS

    meal_types: list[MealType] = Field(
        default_factory=lambda: [
            MealType.BREAKFAST,
            MealType.LUNCH,
            MealType.DINNER,
        ]
    )

    preferred_cuisines: list[Cuisine] = Field(
        default_factory=lambda: [Cuisine.MIXED]
    )

    dietary_preferences: list[DietaryPreference] = Field(
        default_factory=list
    )

    excluded_ingredients: list[str] = Field(
        default_factory=list,
        max_length=30,
    )

    max_total_cooking_minutes_per_meal: int = Field(
        default=60,
        ge=5,
        le=240,
    )

    cost_calculation_mode: CostCalculationMode = (
        CostCalculationMode.PROPORTIONAL
    )

    pantry_items: list[PantryItemInput] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_request(self) -> "MealPlanRequest":
        if len(self.meal_types) != len(set(self.meal_types)):
            raise ValueError(
                "Each meal type can be selected only once."
            )

        if not self.meal_types:
            raise ValueError(
                "At least one meal type must be selected."
            )

        ingredient_ids = [
            item.ingredient_id
            for item in self.pantry_items
        ]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValueError(
                "An ingredient can appear only once in the pantry."
            )

        if (
            self.cost_calculation_mode
            is not CostCalculationMode.PANTRY_AWARE
            and self.pantry_items
        ):
            raise ValueError(
                "Pantry items can only be used in pantry-aware mode."
            )

        return self


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
    price_per_100g_huf: float
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
    seasonal_ratio: float
    ingredients: list[PlannedIngredient]
    instructions: list[str]


class ShoppingListItem(BaseModel):
    ingredient_id: int
    name: str

    required_quantity_grams: float

    pantry_quantity_grams: float
    pantry_used_grams: float

    missing_quantity_grams: float

    package_size_grams: float
    package_price_huf: int

    packages_to_buy: int | None
    purchase_quantity_grams: float | None
    purchase_cost_huf: int | None

    leftover_after_plan_grams: float | None

    proportional_cost_huf: int

    price_store: str
    price_source: str
    price_checked_at: date | None

    seasonal: bool


class PlanSummary(BaseModel):
    people_count: int

    calories_per_person: int
    calorie_target_per_person: int

    cost_calculation_mode: CostCalculationMode

    proportional_total_cost_huf: int
    purchase_total_cost_huf: int | None

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
    shopping_list: list[ShoppingListItem]
    notices: list[str]
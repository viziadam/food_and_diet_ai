from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from itertools import product
from math import ceil, inf

from app.core.exceptions import DomainError
from app.modules.catalog.models import Recipe
from app.modules.catalog.service import CatalogService
from app.modules.planning.schemas import (
    Cuisine,
    DietaryPreference,
    Goal,
    MacroSummary,
    MealPlanRequest,
    MealPlanResponse,
    MealType,
    PlannedIngredient,
    PlannedMeal,
    PlanSummary,
    ShoppingListItem,
    CostCalculationMode,
)

CALORIE_SHARE: dict[MealType, float] = {
    MealType.BREAKFAST: 0.25,
    MealType.LUNCH: 0.40,
    MealType.DINNER: 0.30,
    MealType.SNACK: 0.05,
}


@dataclass(frozen=True)
class RecipeMetrics:
    calories_per_serving: float
    protein_per_serving: float
    carbs_per_serving: float
    fat_per_serving: float
    cost_per_serving: float
    seasonal_ratio: float


class RuleBasedPlanner:
    def create_plan(self, request: MealPlanRequest, recipes: list[Recipe]) -> MealPlanResponse:
        candidates = {
            meal_type: self._candidate_recipes(request, recipes, meal_type)
            for meal_type in request.meal_types
        }
        unavailable = [meal.value for meal, values in candidates.items() if not values]
        if unavailable:
            raise DomainError(
                f"No suitable recipes were found for: {', '.join(unavailable)}.",
                code="NO_FEASIBLE_PLAN",
                status_code=422,
            )

        best_recipes: tuple[Recipe, ...] | None = None
        best_score = inf
        for combination in product(*(candidates[meal][:10] for meal in request.meal_types)):
            score = self._score_combination(request, combination)
            if score < best_score:
                best_score = score
                best_recipes = combination

        if best_recipes is None:
            raise DomainError(
                "No feasible meal plan could be created.",
                code="NO_FEASIBLE_PLAN",
                status_code=422,
            )

        return self._build_response(request, best_recipes)

    def _candidate_recipes(
        self,
        request: MealPlanRequest,
        recipes: list[Recipe],
        meal_type: MealType,
    ) -> list[Recipe]:
        preferred = {c.value for c in request.preferred_cuisines if c is not Cuisine.MIXED}
        excluded = {
            name.strip().casefold() for name in request.excluded_ingredients if name.strip()
        }
        required_tags = self._required_tags(request.dietary_preferences)

        filtered: list[Recipe] = []
        for recipe in recipes:
            if recipe.meal_type != meal_type.value:
                continue
            if (
                recipe.prep_minutes + recipe.cook_minutes
                > request.max_total_cooking_minutes_per_meal
            ):
                continue
            if required_tags and not required_tags.issubset(set(recipe.tags)):
                continue
            if excluded and any(
                any(token in link.ingredient.name.casefold() for token in excluded)
                for link in recipe.ingredients
            ):
                continue
            filtered.append(recipe)

        if preferred:
            preferred_matches = [recipe for recipe in filtered if recipe.cuisine in preferred]
            if preferred_matches:
                filtered = preferred_matches

        target = request.calorie_target_per_person * CALORIE_SHARE[meal_type]
        return sorted(
            filtered, key=lambda recipe: abs(self._metrics(recipe).calories_per_serving - target)
        )
    
    def _aggregate_required_ingredients(
        self,
        request: MealPlanRequest,
        recipes: tuple[Recipe, ...],
    ) -> dict[int, dict[str, object]]:
        aggregated: dict[int, dict[str, object]] = {}

        for recipe in recipes:
            scale = request.people_count / recipe.default_servings

            for link in recipe.ingredients:
                ingredient = link.ingredient
                quantity = link.quantity_grams * scale

                if ingredient.id not in aggregated:
                    aggregated[ingredient.id] = {
                        "ingredient": ingredient,
                        "quantity": 0.0,
                    }

                aggregated[ingredient.id]["quantity"] = (
                    float(aggregated[ingredient.id]["quantity"])
                    + quantity
                )

        return aggregated
    
    def _build_shopping_list(
        self,
        request: MealPlanRequest,
        recipes: tuple[Recipe, ...],
    ) -> list[ShoppingListItem]:
        month = date.today().month

        aggregated = self._aggregate_required_ingredients(
            request,
            recipes,
        )

        pantry_by_ingredient = {
            item.ingredient_id: item.quantity_grams
            for item in request.pantry_items
        }

        shopping_items: list[ShoppingListItem] = []

        for ingredient_id, data in aggregated.items():
            ingredient = data["ingredient"]
            required_quantity = round(
                float(data["quantity"]),
                1,
            )

            if (
                request.cost_calculation_mode
                is CostCalculationMode.PANTRY_AWARE
            ):
                pantry_quantity = pantry_by_ingredient.get(
                    ingredient_id,
                    0.0,
                )
            else:
                pantry_quantity = 0.0

            pantry_used = min(
                required_quantity,
                pantry_quantity,
            )

            missing_quantity = max(
                required_quantity - pantry_used,
                0.0,
            )

            proportional_cost = round(
                required_quantity
                * self._price_per_gram(ingredient)
            )

            packages_to_buy: int | None
            purchase_quantity: float | None
            purchase_cost: int | None
            leftover_after_plan: float | None

            if (
                request.cost_calculation_mode
                is CostCalculationMode.PROPORTIONAL
            ):
                packages_to_buy = None
                purchase_quantity = None
                purchase_cost = None
                leftover_after_plan = None
            else:
                if missing_quantity > 0:
                    packages_to_buy = ceil(
                        missing_quantity
                        / ingredient.package_size_grams
                    )
                else:
                    packages_to_buy = 0

                purchase_quantity = (
                    packages_to_buy
                    * ingredient.package_size_grams
                )

                purchase_cost = (
                    packages_to_buy
                    * ingredient.package_price_huf
                )

                leftover_after_plan = round(
                    pantry_quantity
                    + purchase_quantity
                    - required_quantity,
                    1,
                )

            seasonal = (
                not ingredient.seasonal_months
                or month in ingredient.seasonal_months
            )

            shopping_items.append(
                ShoppingListItem(
                    ingredient_id=ingredient.id,
                    name=ingredient.name,
                    required_quantity_grams=required_quantity,
                    pantry_quantity_grams=round(
                        pantry_quantity,
                        1,
                    ),
                    pantry_used_grams=round(
                        pantry_used,
                        1,
                    ),
                    missing_quantity_grams=round(
                        missing_quantity,
                        1,
                    ),
                    package_size_grams=ingredient.package_size_grams,
                    package_price_huf=ingredient.package_price_huf,
                    packages_to_buy=packages_to_buy,
                    purchase_quantity_grams=purchase_quantity,
                    purchase_cost_huf=purchase_cost,
                    leftover_after_plan_grams=leftover_after_plan,
                    proportional_cost_huf=proportional_cost,
                    price_store=ingredient.price_store,
                    price_source=ingredient.price_source,
                    price_checked_at=ingredient.price_checked_at,
                    seasonal=seasonal,
                )
            )

        return sorted(
            shopping_items,
            key=lambda item: item.name.casefold(),
        )
    
    def _combination_cost(
        self,
        request: MealPlanRequest,
        recipes: tuple[Recipe, ...],
    ) -> float:
        shopping_list = self._build_shopping_list(
            request,
            recipes,
        )

        if (
            request.cost_calculation_mode
            is CostCalculationMode.PROPORTIONAL
        ):
            return float(
                sum(
                    item.proportional_cost_huf
                    for item in shopping_list
                )
            )

        return float(
            sum(
                item.purchase_cost_huf or 0
                for item in shopping_list
            )
        )

    def _score_combination(self, request: MealPlanRequest, recipes: tuple[Recipe, ...]) -> float:
        metrics = [self._metrics(recipe) for recipe in recipes]
        calories = sum(item.calories_per_serving for item in metrics)
        protein = sum(item.protein_per_serving for item in metrics)
        household_cost = self._combination_cost(request, recipes)
        seasonal = sum(item.seasonal_ratio for item in metrics) / len(metrics)

        score = abs(calories - request.calorie_target_per_person) * 1.4
        if household_cost > request.daily_budget_huf:
            score += (household_cost - request.daily_budget_huf) * 8
        else:
            score += (request.daily_budget_huf - household_cost) * 0.02
        score -= seasonal * 140

        if request.goal is Goal.HIGH_PROTEIN:
            score -= protein * 5
        elif request.goal is Goal.WEIGHT_LOSS:
            score += max(0, calories - request.calorie_target_per_person) * 3
            score -= sum("light" in recipe.tags for recipe in recipes) * 60

        repeated_main_categories = len(recipes) - len(
            {recipe.ingredients[0].ingredient.category for recipe in recipes if recipe.ingredients}
        )
        score += repeated_main_categories * 45
        return score

    def _build_response(
        self,
        request: MealPlanRequest,
        recipes: tuple[Recipe, ...],
    ) -> MealPlanResponse:
        month = date.today().month
        planned_meals: list[PlannedMeal] = []
        shopping: dict[str, dict[str, float | bool]] = defaultdict(
            lambda: {"quantity": 0.0, "cost": 0.0, "seasonal": True}
        )
        total_calories = total_protein = total_carbs = total_fat = total_cost = 0.0
        seasonal_weight = ingredient_weight = 0.0

        for recipe in recipes:
            metrics = self._metrics(recipe)
            scale = request.people_count / recipe.default_servings
            ingredients: list[PlannedIngredient] = []
            for link in recipe.ingredients:
                quantity = round(link.quantity_grams * scale, 1)
                cost = round(quantity / 100 * link.ingredient.price_per_100g_huf)
                seasonal = (
                    not link.ingredient.seasonal_months or month in link.ingredient.seasonal_months
                )
                ingredients.append(
                    PlannedIngredient(
                        name=link.ingredient.name,
                        quantity_grams=quantity,
                        display_quantity=link.display_quantity,
                        estimated_cost_huf=cost,
                        seasonal=seasonal,
                    )
                )
                item = shopping[link.ingredient.name]
                item["quantity"] = float(item["quantity"]) + quantity
                item["cost"] = float(item["cost"]) + cost
                item["seasonal"] = bool(item["seasonal"]) and seasonal
                seasonal_weight += quantity if seasonal else 0
                ingredient_weight += quantity

            meal_cost = round(metrics.cost_per_serving * request.people_count)
            total_cost += meal_cost
            total_calories += metrics.calories_per_serving
            total_protein += metrics.protein_per_serving
            total_carbs += metrics.carbs_per_serving
            total_fat += metrics.fat_per_serving
            planned_meals.append(
                PlannedMeal(
                    recipe_id=recipe.id,
                    name=recipe.name,
                    description=recipe.description,
                    meal_type=MealType(recipe.meal_type),
                    cuisine=Cuisine(recipe.cuisine),
                    servings=request.people_count,
                    prep_minutes=recipe.prep_minutes,
                    cook_minutes=recipe.cook_minutes,
                    nutrition_per_person=MacroSummary(
                        calories_kcal=round(metrics.calories_per_serving),
                        protein_g=round(metrics.protein_per_serving, 1),
                        carbs_g=round(metrics.carbs_per_serving, 1),
                        fat_g=round(metrics.fat_per_serving, 1),
                    ),
                    estimated_cost_huf=meal_cost,
                    seasonal_ratio=round(metrics.seasonal_ratio, 2),
                    ingredients=ingredients,
                    instructions=recipe.instructions,
                )
            )

        shopping_list = [
            ShoppingListItem(
                name=name,
                quantity_grams=round(float(data["quantity"]), 1),
                estimated_cost_huf=round(float(data["cost"])),
                seasonal=bool(data["seasonal"]),
            )
            for name, data in sorted(shopping.items())
        ]
        rounded_cost = round(total_cost)
        seasonal_ratio = seasonal_weight / ingredient_weight if ingredient_weight else 0.0
        notices = [
            (
                "A tápértékek és árak becslések; a termékcímkét és az aktuális "
                "bolti árat mindig ellenőrizd."
            ),
            (
                "Ez a szolgáltatás háztartási étkezéstervező, nem helyettesít "
                "orvosi vagy dietetikusi tanácsadást."
            ),
        ]
        if rounded_cost > request.daily_budget_huf:
            notices.append(
                "A megadott korlátozások mellett a legjobb elérhető terv "
                "kissé meghaladja a keretet."
            )
        calorie_difference = abs(total_calories - request.calorie_target_per_person)
        if calorie_difference > request.calorie_target_per_person * 0.1:
            notices.append(
                "A jelenlegi receptkészletből összeállított terv több mint 10%-kal eltér "
                "a kalóriacéltól; a következő verzióban az adagoptimalizálás ezt tovább finomítja."
            )

        return MealPlanResponse(
            id="",
            summary=PlanSummary(
                people_count=request.people_count,
                calories_per_person=round(total_calories),
                calorie_target_per_person=request.calorie_target_per_person,
                estimated_total_cost_huf=rounded_cost,
                budget_huf=request.daily_budget_huf,
                budget_difference_huf=request.daily_budget_huf - rounded_cost,
                protein_per_person_g=round(total_protein, 1),
                carbs_per_person_g=round(total_carbs, 1),
                fat_per_person_g=round(total_fat, 1),
                seasonal_ingredient_ratio=round(seasonal_ratio, 2),
            ),
            meals=planned_meals,
            shopping_list=shopping_list,
            notices=notices,
        )

    @staticmethod
    def _required_tags(preferences: list[DietaryPreference]) -> set[str]:
        mapping = {
            DietaryPreference.VEGETARIAN: "vegetarian",
            DietaryPreference.LACTOSE_FREE: "lactose_free",
            DietaryPreference.GLUTEN_FREE: "gluten_free",
        }
        return {mapping[item] for item in preferences}
    
    @staticmethod
    def _price_per_gram(ingredient) -> float:
        if (
            ingredient.package_size_grams > 0
            and ingredient.package_price_huf > 0
        ):
            return (
                ingredient.package_price_huf
                / ingredient.package_size_grams
            )

        return ingredient.price_per_100g_huf / 100

    @staticmethod
    def _metrics(recipe: Recipe) -> RecipeMetrics:
        calories = protein = carbs = fat = cost = 0.0
        for link in recipe.ingredients:
            multiplier = link.quantity_grams / 100
            ingredient = link.ingredient
            calories += ingredient.kcal_per_100g * multiplier
            protein += ingredient.protein_per_100g * multiplier
            carbs += ingredient.carbs_per_100g * multiplier
            fat += ingredient.fat_per_100g * multiplier
            cost += (link.quantity_grams* RuleBasedPlanner._price_per_gram(ingredient))
        servings = max(recipe.default_servings, 1)
        return RecipeMetrics(
            calories_per_serving=calories / servings,
            protein_per_serving=protein / servings,
            carbs_per_serving=carbs / servings,
            fat_per_serving=fat / servings,
            cost_per_serving=cost / servings,
            seasonal_ratio=CatalogService.seasonal_ratio(recipe),
        )

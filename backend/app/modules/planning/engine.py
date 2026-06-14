from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from itertools import product
from math import ceil, inf

from app.core.exceptions import DomainError
from app.modules.catalog.models import Ingredient, Recipe
from app.modules.catalog.service import CatalogService
from app.modules.planning.schemas import (
    Cuisine,
    DietaryPreference,
    Goal,
    MacroSummary,
    MealOptionGroup,
    MealPlanRequest,
    MealPlanResponse,
    MealType,
    PlannedIngredient,
    PlannedMeal,
    PlanSummary,
    ShoppingListItem,
)

OPTION_COUNT = 3
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


@dataclass
class AggregatedIngredient:
    ingredient: Ingredient
    quantity_grams: float = 0.0
    seasonal: bool = True


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

        option_recipes = {
            meal_type: values[:OPTION_COUNT] for meal_type, values in candidates.items()
        }
        best_recipes: tuple[Recipe, ...] | None = None
        best_score = inf
        for combination in product(*(option_recipes[meal] for meal in request.meal_types)):
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

        planned_options: dict[MealType, list[PlannedMeal]] = {
            meal_type: [self._build_planned_meal(request, recipe) for recipe in values]
            for meal_type, values in option_recipes.items()
        }
        selected_meals = [self._build_planned_meal(request, recipe) for recipe in best_recipes]
        shopping_list = self._build_shopping_list(request, best_recipes)
        summary = self._build_summary(request, selected_meals, shopping_list)
        option_groups = [
            MealOptionGroup(
                meal_type=meal_type,
                recommended_recipe_id=best_recipes[index].id,
                options=planned_options[meal_type],
            )
            for index, meal_type in enumerate(request.meal_types)
        ]

        return MealPlanResponse(
            id="",
            summary=summary,
            meals=selected_meals,
            meal_options=option_groups,
            shopping_list=shopping_list,
            notices=self._build_notices(request, summary, option_groups),
        )

    def _candidate_recipes(
        self,
        request: MealPlanRequest,
        recipes: list[Recipe],
        meal_type: MealType,
    ) -> list[Recipe]:
        preferred = {cuisine.value for cuisine in request.preferred_cuisines if cuisine is not Cuisine.MIXED}
        excluded = {
            name.strip().casefold() for name in request.excluded_ingredients if name.strip()
        }
        required_tags = self._required_tags(request.dietary_preferences)
        filtered: list[Recipe] = []

        for recipe in recipes:
            if recipe.meal_type != meal_type.value:
                continue
            if recipe.prep_minutes + recipe.cook_minutes > request.max_total_cooking_minutes_per_meal:
                continue
            if required_tags and not required_tags.issubset(set(recipe.tags)):
                continue
            if excluded and any(
                any(token in link.ingredient.name.casefold() for token in excluded)
                for link in recipe.ingredients
            ):
                continue
            filtered.append(recipe)

        target = request.calorie_target_per_person * CALORIE_SHARE[meal_type]
        return sorted(
            filtered,
            key=lambda recipe: self._recipe_score(request, recipe, target, preferred),
        )

    def _recipe_score(
        self,
        request: MealPlanRequest,
        recipe: Recipe,
        target_calories: float,
        preferred_cuisines: set[str],
    ) -> float:
        metrics = self._metrics(recipe)
        score = abs(metrics.calories_per_serving - target_calories) * 1.3
        if preferred_cuisines and recipe.cuisine not in preferred_cuisines:
            score += 120
        score -= metrics.seasonal_ratio * 50
        if request.goal is Goal.HIGH_PROTEIN:
            score -= metrics.protein_per_serving * 3
        elif request.goal is Goal.WEIGHT_LOSS and "light" in recipe.tags:
            score -= 35
        return score

    def _score_combination(
        self,
        request: MealPlanRequest,
        recipes: tuple[Recipe, ...],
    ) -> float:
        metrics = [self._metrics(recipe) for recipe in recipes]
        calories = sum(item.calories_per_serving for item in metrics)
        protein = sum(item.protein_per_serving for item in metrics)
        purchase_cost = sum(
            item.purchase_cost_huf for item in self._build_shopping_list(request, recipes)
        )
        seasonal = sum(item.seasonal_ratio for item in metrics) / len(metrics)

        score = abs(calories - request.calorie_target_per_person) * 1.4
        if purchase_cost > request.daily_budget_huf:
            score += (purchase_cost - request.daily_budget_huf) * 2.2
        score -= seasonal * 140
        if request.goal is Goal.HIGH_PROTEIN:
            score -= protein * 5
        elif request.goal is Goal.WEIGHT_LOSS:
            score += max(0, calories - request.calorie_target_per_person) * 3

        main_categories = {
            recipe.ingredients[0].ingredient.category
            for recipe in recipes
            if recipe.ingredients
        }
        return score + (len(recipes) - len(main_categories)) * 45

    def _build_planned_meal(
        self,
        request: MealPlanRequest,
        recipe: Recipe,
    ) -> PlannedMeal:
        month = date.today().month
        metrics = self._metrics(recipe)
        scale = request.people_count / max(recipe.default_servings, 1)
        ingredients: list[PlannedIngredient] = []
        purchase_cost = 0

        for link in recipe.ingredients:
            ingredient = link.ingredient
            quantity = round(link.quantity_grams * scale, 1)
            package_size = self._package_size(ingredient)
            package_price = self._package_price(ingredient)
            packages = self._packages_needed(quantity, package_size)
            purchase_cost += packages * package_price
            seasonal = not ingredient.seasonal_months or month in ingredient.seasonal_months
            ingredients.append(
                PlannedIngredient(
                    ingredient_id=ingredient.id,
                    name=ingredient.name,
                    quantity_grams=quantity,
                    display_quantity=f"{quantity:g} g",
                    estimated_cost_huf=round(quantity * self._price_per_gram(ingredient)),
                    package_size_grams=package_size,
                    package_price_huf=package_price,
                    price_store=ingredient.price_store,
                    price_source=ingredient.price_source,
                    price_checked_at=ingredient.price_checked_at,
                    seasonal=seasonal,
                )
            )

        return PlannedMeal(
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
            estimated_cost_huf=round(metrics.cost_per_serving * request.people_count),
            purchase_cost_huf=purchase_cost,
            seasonal_ratio=round(metrics.seasonal_ratio, 2),
            ingredients=ingredients,
            instructions=recipe.instructions,
        )

    def _build_shopping_list(
        self,
        request: MealPlanRequest,
        recipes: tuple[Recipe, ...],
    ) -> list[ShoppingListItem]:
        month = date.today().month
        aggregated: dict[int, AggregatedIngredient] = {}

        for recipe in recipes:
            scale = request.people_count / max(recipe.default_servings, 1)
            for link in recipe.ingredients:
                ingredient = link.ingredient
                seasonal = not ingredient.seasonal_months or month in ingredient.seasonal_months
                item = aggregated.setdefault(
                    ingredient.id,
                    AggregatedIngredient(ingredient=ingredient),
                )
                item.quantity_grams += link.quantity_grams * scale
                item.seasonal = item.seasonal and seasonal

        shopping_list: list[ShoppingListItem] = []
        for item in aggregated.values():
            ingredient = item.ingredient
            required = round(item.quantity_grams, 1)
            package_size = self._package_size(ingredient)
            package_price = self._package_price(ingredient)
            packages = self._packages_needed(required, package_size)
            purchase_quantity = packages * package_size
            shopping_list.append(
                ShoppingListItem(
                    ingredient_id=ingredient.id,
                    name=ingredient.name,
                    required_quantity_grams=required,
                    package_size_grams=package_size,
                    package_price_huf=package_price,
                    packages_to_buy=packages,
                    purchase_quantity_grams=round(purchase_quantity, 1),
                    proportional_cost_huf=round(required * self._price_per_gram(ingredient)),
                    purchase_cost_huf=packages * package_price,
                    leftover_after_plan_grams=round(purchase_quantity - required, 1),
                    price_store=ingredient.price_store,
                    price_source=ingredient.price_source,
                    price_checked_at=ingredient.price_checked_at,
                    seasonal=item.seasonal,
                )
            )

        return sorted(shopping_list, key=lambda value: value.name.casefold())

    @staticmethod
    def _build_summary(
        request: MealPlanRequest,
        meals: list[PlannedMeal],
        shopping_list: list[ShoppingListItem],
    ) -> PlanSummary:
        calories = sum(meal.nutrition_per_person.calories_kcal for meal in meals)
        protein = sum(meal.nutrition_per_person.protein_g for meal in meals)
        carbs = sum(meal.nutrition_per_person.carbs_g for meal in meals)
        fat = sum(meal.nutrition_per_person.fat_g for meal in meals)
        proportional = sum(item.proportional_cost_huf for item in shopping_list)
        full_purchase = sum(item.purchase_cost_huf for item in shopping_list)
        seasonal_quantity = sum(
            item.required_quantity_grams for item in shopping_list if item.seasonal
        )
        total_quantity = sum(item.required_quantity_grams for item in shopping_list)
        seasonal_ratio = seasonal_quantity / total_quantity if total_quantity else 0.0

        return PlanSummary(
            people_count=request.people_count,
            calories_per_person=round(calories),
            calorie_target_per_person=request.calorie_target_per_person,
            proportional_total_cost_huf=round(proportional),
            full_purchase_total_cost_huf=round(full_purchase),
            shopping_total_cost_huf=round(full_purchase),
            estimated_total_cost_huf=round(proportional),
            budget_huf=request.daily_budget_huf,
            budget_difference_huf=request.daily_budget_huf - round(full_purchase),
            protein_per_person_g=round(protein, 1),
            carbs_per_person_g=round(carbs, 1),
            fat_per_person_g=round(fat, 1),
            seasonal_ingredient_ratio=round(seasonal_ratio, 2),
        )

    @staticmethod
    def _build_notices(
        request: MealPlanRequest,
        summary: PlanSummary,
        groups: list[MealOptionGroup],
    ) -> list[str]:
        notices = [
            (
                "Az arányos költség a ténylegesen felhasznált mennyiséget, a teljes "
                "vásárlás pedig a szükséges egész csomagokat mutatja."
            ),
            (
                "Az MVP árai kézzel rögzített demoárak; az aktuális bolti árat mindig "
                "ellenőrizd vásárlás előtt."
            ),
            (
                "Ez a szolgáltatás háztartási étkezéstervező, nem helyettesít orvosi "
                "vagy dietetikusi tanácsadást."
            ),
        ]
        if summary.full_purchase_total_cost_huf > request.daily_budget_huf:
            notices.append("A teljes csomagok megvásárlása meghaladja a megadott keretet.")
        for group in groups:
            if len(group.options) < OPTION_COUNT:
                notices.append(
                    f"A(z) {group.meal_type.value} étkezéshez a korlátozások mellett "
                    f"csak {len(group.options)} recept érhető el."
                )
        return notices

    @staticmethod
    def _required_tags(preferences: list[DietaryPreference]) -> set[str]:
        mapping = {
            DietaryPreference.VEGETARIAN: "vegetarian",
            DietaryPreference.LACTOSE_FREE: "lactose_free",
            DietaryPreference.GLUTEN_FREE: "gluten_free",
        }
        return {mapping[item] for item in preferences}

    @staticmethod
    def _packages_needed(quantity_grams: float, package_size_grams: float) -> int:
        if quantity_grams <= 0:
            return 0
        return ceil(quantity_grams / package_size_grams)

    @staticmethod
    def _package_size(ingredient: Ingredient) -> float:
        return ingredient.package_size_grams if ingredient.package_size_grams > 0 else 100.0

    def _package_price(self, ingredient: Ingredient) -> int:
        if ingredient.package_price_huf > 0:
            return ingredient.package_price_huf
        return round(self._package_size(ingredient) * self._price_per_gram(ingredient))

    @staticmethod
    def _price_per_gram(ingredient: Ingredient) -> float:
        if ingredient.package_size_grams > 0 and ingredient.package_price_huf > 0:
            return ingredient.package_price_huf / ingredient.package_size_grams
        return ingredient.price_per_100g_huf / 100

    def _metrics(self, recipe: Recipe) -> RecipeMetrics:
        calories = protein = carbs = fat = cost = 0.0
        for link in recipe.ingredients:
            multiplier = link.quantity_grams / 100
            ingredient = link.ingredient
            calories += ingredient.kcal_per_100g * multiplier
            protein += ingredient.protein_per_100g * multiplier
            carbs += ingredient.carbs_per_100g * multiplier
            fat += ingredient.fat_per_100g * multiplier
            cost += link.quantity_grams * self._price_per_gram(ingredient)
        servings = max(recipe.default_servings, 1)
        return RecipeMetrics(
            calories_per_serving=calories / servings,
            protein_per_serving=protein / servings,
            carbs_per_serving=carbs / servings,
            fat_per_serving=fat / servings,
            cost_per_serving=cost / servings,
            seasonal_ratio=CatalogService.seasonal_ratio(recipe),
        )

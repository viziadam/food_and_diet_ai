```python
from dataclasses import dataclass

from app.modules.catalog.models import Ingredient, Recipe
from app.modules.catalog.service import CatalogService


@dataclass(frozen=True)
class RecipeMetrics:
    calories_per_serving: float
    protein_per_serving: float
    carbs_per_serving: float
    fat_per_serving: float
    cost_per_serving: float
    seasonal_ratio: float


def price_per_gram(ingredient: Ingredient) -> float:
    if ingredient.package_size_grams > 0 and ingredient.package_price_huf > 0:
        return ingredient.package_price_huf / ingredient.package_size_grams
    return ingredient.price_per_100g_huf / 100


def recipe_metrics(recipe: Recipe) -> RecipeMetrics:
    calories = protein = carbs = fat = cost = 0.0
    for link in recipe.ingredients:
        multiplier = link.quantity_grams / 100
        ingredient = link.ingredient
        calories += ingredient.kcal_per_100g * multiplier
        protein += ingredient.protein_per_100g * multiplier
        carbs += ingredient.carbs_per_100g * multiplier
        fat += ingredient.fat_per_100g * multiplier
        cost += link.quantity_grams * price_per_gram(ingredient)
    servings = max(recipe.default_servings, 1)
    return RecipeMetrics(
        calories_per_serving=calories / servings,
        protein_per_serving=protein / servings,
        carbs_per_serving=carbs / servings,
        fat_per_serving=fat / servings,
        cost_per_serving=cost / servings,
        seasonal_ratio=CatalogService.seasonal_ratio(recipe),
    )
```

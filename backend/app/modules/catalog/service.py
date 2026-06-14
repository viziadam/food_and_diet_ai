from datetime import date

from app.modules.catalog.models import Recipe
from app.modules.catalog.repository import RecipeRepository
from app.modules.catalog.schemas import RecipeSummary


class CatalogService:
    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    def list_recipes(self) -> list[RecipeSummary]:
        return [self._to_summary(recipe) for recipe in self._repository.list_all()]

    @staticmethod
    def seasonal_ratio(recipe: Recipe, month: int | None = None) -> float:
        selected_month = month or date.today().month
        ingredients = recipe.ingredients
        if not ingredients:
            return 0.0
        seasonal = sum(
            1
            for link in ingredients
            if not link.ingredient.seasonal_months
            or selected_month in link.ingredient.seasonal_months
        )
        return seasonal / len(ingredients)

    @staticmethod
    def _to_summary(recipe: Recipe) -> RecipeSummary:
        return RecipeSummary(
            id=recipe.id,
            slug=recipe.slug,
            name=recipe.name,
            description=recipe.description,
            meal_type=recipe.meal_type,
            cuisine=recipe.cuisine,
            prep_minutes=recipe.prep_minutes,
            cook_minutes=recipe.cook_minutes,
            tags=recipe.tags,
        )

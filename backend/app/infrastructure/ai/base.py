from typing import Protocol

from app.modules.planning.schemas import MealPlanRequest, MealPlanResponse


class MealPlanNarrativeProvider(Protocol):
    """Extension point for OpenAI, Ollama or another structured-output provider."""

    def enrich(
        self,
        request: MealPlanRequest,
        plan: MealPlanResponse,
    ) -> MealPlanResponse:
        """Add explanatory text without changing verified numeric values."""
        ...

from app.modules.planning.schemas import MealPlanRequest, MealPlanResponse


class PassthroughNarrativeProvider:
    """MVP fallback used until an external language model is configured."""

    def enrich(
        self,
        request: MealPlanRequest,
        plan: MealPlanResponse,
    ) -> MealPlanResponse:
        del request
        return plan

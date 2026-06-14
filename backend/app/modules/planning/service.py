from uuid import uuid4

from app.core.exceptions import DomainError
from app.modules.catalog.models import MealPlanRecord
from app.modules.catalog.repository import MealPlanRepository, RecipeRepository
from app.modules.planning.engine import RuleBasedPlanner
from app.modules.planning.schemas import MealPlanRequest, MealPlanResponse


class PlanningService:
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        plan_repository: MealPlanRepository,
        planner: RuleBasedPlanner,
    ) -> None:
        self._recipe_repository = recipe_repository
        self._plan_repository = plan_repository
        self._planner = planner

    def generate(self, request: MealPlanRequest) -> MealPlanResponse:
        response = self._planner.create_plan(request, self._recipe_repository.list_all())
        response.id = str(uuid4())
        record = MealPlanRecord(
            id=response.id,
            request_snapshot=request.model_dump(mode="json"),
            result_snapshot=response.model_dump(mode="json"),
        )
        self._plan_repository.save(record)
        return response

    def get(self, plan_id: str) -> MealPlanResponse:
        record = self._plan_repository.get(plan_id)
        if record is None:
            raise DomainError("Meal plan not found.", code="PLAN_NOT_FOUND", status_code=404)
        return MealPlanResponse.model_validate(record.result_snapshot)

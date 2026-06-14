from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.catalog.repository import MealPlanRepository, RecipeRepository
from app.modules.planning.engine import RuleBasedPlanner
from app.modules.planning.schemas import MealPlanRequest, MealPlanResponse
from app.modules.planning.service import PlanningService

router = APIRouter(prefix="/plans", tags=["Meal plans"])


def get_planning_service(session: Annotated[Session, Depends(get_db)]) -> PlanningService:
    return PlanningService(
        RecipeRepository(session),
        MealPlanRepository(session),
        RuleBasedPlanner(),
    )


@router.post("/generate", response_model=MealPlanResponse, status_code=201)
def generate_plan(
    request: MealPlanRequest,
    service: Annotated[PlanningService, Depends(get_planning_service)],
) -> MealPlanResponse:
    return service.generate(request)


@router.get("/{plan_id}", response_model=MealPlanResponse)
def get_plan(
    plan_id: str,
    service: Annotated[PlanningService, Depends(get_planning_service)],
) -> MealPlanResponse:
    return service.get(plan_id)

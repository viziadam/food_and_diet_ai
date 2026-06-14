from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.catalog.models import MealPlanRecord, Recipe, RecipeIngredient


class RecipeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Recipe]:
        statement = select(Recipe).options(
            selectinload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)
        )
        return list(self._session.scalars(statement).unique().all())


class MealPlanRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, record: MealPlanRecord) -> MealPlanRecord:
        self._session.add(record)
        self._session.commit()
        self._session.refresh(record)
        return record

    def get(self, plan_id: str) -> MealPlanRecord | None:
        return self._session.get(MealPlanRecord, plan_id)

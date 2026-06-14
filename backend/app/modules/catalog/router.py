from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.catalog.repository import RecipeRepository
from app.modules.catalog.schemas import RecipeSummary
from app.modules.catalog.service import CatalogService

router = APIRouter(prefix="/catalog", tags=["Catalog"])


def get_catalog_service(session: Annotated[Session, Depends(get_db)]) -> CatalogService:
    return CatalogService(RecipeRepository(session))


@router.get("/recipes", response_model=list[RecipeSummary])
def list_recipes(
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> list[RecipeSummary]:
    return service.list_recipes()

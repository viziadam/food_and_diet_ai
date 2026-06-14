from fastapi import APIRouter

from app.modules.catalog.router import router as catalog_router
from app.modules.health.router import router as health_router
from app.modules.planning.router import router as planning_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(catalog_router)
api_router.include_router(planning_router)

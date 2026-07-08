from fastapi import APIRouter

from app.api.v1.routes.tasks import router as tasks_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(tasks_router, tags=["tasks"])

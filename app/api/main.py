from fastapi import APIRouter

from app.api.endpoints import files

api_router = APIRouter()
api_router.include_router(files.router, tags=["files"], prefix="/files")

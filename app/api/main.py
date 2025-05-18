from fastapi import APIRouter

from app.api.endpoints import files, protein

api_router = APIRouter()
api_router.include_router(files.router, tags=["files"], prefix="/files")
api_router.include_router(protein.router, tags=["proteins"], prefix="/proteins")

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.projects import router as projects_router
from app.api.v1.endpoints.assets import router as assets_router
from app.api.v1.endpoints.vulnerabilities import router as vulnerabilities_router
from app.api.v1.endpoints.scans import router as scans_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(projects_router)
api_router.include_router(assets_router)
api_router.include_router(vulnerabilities_router)
api_router.include_router(scans_router)
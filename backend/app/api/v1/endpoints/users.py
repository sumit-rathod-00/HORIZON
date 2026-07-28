from fastapi import APIRouter, Depends

from app.models.user import User
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me")
async def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user
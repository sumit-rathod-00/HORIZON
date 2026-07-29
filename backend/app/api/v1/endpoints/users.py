from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.security.dependencies import get_current_user
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserRead,
)
async def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.patch(
    "/me",
    response_model=UserRead,
)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    auth_service = AuthService(db)

    updated_user = await auth_service.update_profile(
        user=current_user,
        full_name=user_update.full_name,
    )

    return updated_user

@router.patch(
    "/me",
    response_model=UserRead,
)
async def update_current_user(
    data: UserUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = AuthService(session)

    return await service.update_current_user(
        current_user,
        data.full_name,
    )
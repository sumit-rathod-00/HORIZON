from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import HTTPException, status

from app.db.session import get_db
from app.services.auth_service import AuthService
from app.security.dependencies import (get_current_admin,get_current_user,)
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

@router.get(
    "/",
    response_model=list[UserRead],
)
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    auth_service = AuthService(db)
    return await auth_service.get_all_users()

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    auth_service = AuthService(db)

    deleted = await auth_service.delete_user_by_id(user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
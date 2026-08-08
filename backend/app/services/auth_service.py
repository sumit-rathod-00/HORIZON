from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security.password import hash_password, verify_password
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    UnauthorizedException,
    UserNotFoundException,
)


class AuthService:
    """Business logic layer for authentication-related use cases."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repository = UserRepository(session)

    async def register(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> User:

        existing_user = await self._user_repository.get_by_email(email)

        if existing_user is not None:
            raise ConflictException("Email already registered")

        hashed_password = hash_password(password)

        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
        )

        try:
            created_user = await self._user_repository.create(user)
            await self._session.commit()
            return created_user

        except Exception:
            await self._session.rollback()
            raise

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> User:
        """Authenticate a user by email and password."""

        user = await self._user_repository.get_by_email(email)

        if user is None:
            raise UnauthorizedException(
                "Incorrect email or password"
            )

        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException(
                "Incorrect email or password"
            )

        if not user.is_active:
            raise UnauthorizedException(
             "User account is inactive"
            )

        return user

    async def update_current_user(
        self,
        user: User,
        full_name: str | None,
    ) -> User:

        return await self._user_repository.update(
        user,
        full_name,
    )

    async def get_all_users(self) -> list[User]:
        """Return all registered users."""
        return await self._user_repository.get_all()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Return a user by ID."""
        return await self._user_repository.get_by_id(user_id)

    async def delete_user(self, user: User) -> None:
        """Delete a user."""
        await self._user_repository.delete(user)

    async def delete_user_by_id(
        self,
        user_id: UUID,
    ) -> None:
        deleted = await self._user_repository.delete_by_id(user_id)

        if not deleted:
            raise UserNotFoundException()

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> User:

        if not verify_password(
            current_password,
            user.hashed_password,
        ):
            raise BadRequestException(
                "Current password is incorrect"
            )

        user.hashed_password = hash_password(new_password)

        await self._session.commit()
        await self._session.refresh(user)

        return user
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security.password import hash_password
from app.security.password import verify_password


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
            raise ValueError("Email already registered")

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
    ) -> Optional[User]:
        """Authenticate a user by email and password."""

        user = await self._user_repository.get_by_email(email)

        if user is None:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    async def update_profile(
        self,
        user: User,
        full_name: str | None,
    ):
        updated_user = await self._user_repository.update(
        user,
        full_name,
    )

        return updated_user

    async def update_current_user(
        self,
        user: User,
        full_name: str | None,
    ) -> User:

        return await self._user_repository.update(
        user,
        full_name,
    )
"""
SQLAlchemy 2.x model for the User entity.

Defines the `User` table used for authentication and account management.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """Represents an application user."""

    __tablename__ = "users"

    # Primary key: server-generated UUID.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Unique, indexed, required identifier for login.
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    # Hashed password only — never store plaintext credentials.
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Optional display name.
    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Account status flags.
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Timezone-aware audit timestamps, managed at the database level.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
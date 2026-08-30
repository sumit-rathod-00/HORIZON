"""Audit log repository for security event logging."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditLogRepository:
    """Repository for audit log operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, audit_log: AuditLog) -> AuditLog:
        """Create a new audit log entry."""
        self._session.add(audit_log)
        await self._session.flush()
        await self._session.refresh(audit_log)
        return audit_log

    async def get_by_actor(
        self,
        actor_id: UUID,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get audit logs for a specific actor."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.actor_id == actor_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_action(
        self,
        action: str,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get audit logs for a specific action type."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.action == action)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 100) -> list[AuditLog]:
        """Get recent audit logs."""
        stmt = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

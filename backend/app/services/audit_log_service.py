"""Audit logging service for security events."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository

logger = logging.getLogger(__name__)


class AuditLogService:
    """Service for creating and managing audit logs."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = AuditLogRepository(session)

    async def log_event(
        self,
        action: str,
        actor_id: UUID | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        result: str = "success",
        details: str | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        """
        Log a security event.

        Args:
            action: The action performed (e.g., "device.enroll", "device.revoke", "auth.login")
            actor_id: The user who performed the action
            target_type: The type of resource affected (e.g., "device", "user")
            target_id: The ID of the resource affected
            result: The result of the action ("success" or "failure")
            details: Additional details about the event (NO SECRETS)
            ip_address: The IP address of the actor

        Returns:
            The created audit log entry
        """
        audit_log = AuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            result=result,
            details=details,
            ip_address=ip_address,
            created_at=datetime.now(timezone.utc),
        )

        created = await self._repository.create(audit_log)
        await self._session.commit()

        logger.info(
            "Audit log created: action=%s actor_id=%s result=%s",
            action,
            actor_id,
            result,
        )

        return created

    async def get_user_logs(self, actor_id: UUID, limit: int = 100) -> list[AuditLog]:
        """Get audit logs for a specific user."""
        return await self._repository.get_by_actor(actor_id, limit)

    async def get_logs_by_action(self, action: str, limit: int = 100) -> list[AuditLog]:
        """Get audit logs for a specific action type."""
        return await self._repository.get_by_action(action, limit)

    async def get_recent_logs(self, limit: int = 100) -> list[AuditLog]:
        """Get recent audit logs."""
        return await self._repository.get_recent(limit)

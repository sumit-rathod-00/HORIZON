from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository


class AssetService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = AssetRepository(session)

    async def create_asset(
        self,
        project_id: UUID,
        name: str,
        asset_type: str,
        ip_address: str | None = None,
    ) -> Asset:

        asset = Asset(
            project_id=project_id,
            name=name,
            asset_type=asset_type,
            ip_address=ip_address,
        )

        created_asset = await self._repository.create(asset)

        await self._session.commit()

        return created_asset

    async def list_assets(
        self,
        project_id: UUID,
    ):
        return await self._repository.get_by_project(project_id)
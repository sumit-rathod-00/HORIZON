from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ProjectNotFoundException
from app.models.asset import Asset
from app.models.user import User
from app.repositories.asset_repository import AssetRepository
from app.repositories.project_repository import ProjectRepository


class AssetService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = AssetRepository(session)
        self._project_repository = ProjectRepository(session)

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

    async def delete_asset(
        self,
        asset_id: UUID,
        owner_id: UUID,
    ) -> None:
        asset = await self._repository.get_by_id(
            asset_id
        )
        if asset is None:
            return
        project = await self._project_repository.get_by_id_and_owner(
            project_id=asset.project_id,
            owner_id=owner_id,
        )
        if project is None:
            raise ProjectNotFoundException()
        await self._repository.delete(asset)
        await self._session.commit()

    async def update_asset(
        self,
        asset_id: UUID,
        owner_id: UUID,
        name: str | None = None,
        asset_type: str | None = None,
        ip_address: str | None = None,
    ) -> Asset:
        asset = await self._repository.get_by_id(
            asset_id
        )
        if asset is None:
            raise ProjectNotFoundException()
        project = await self._project_repository.get_by_id_and_owner(
            project_id=asset.project_id,
            owner_id=owner_id,
        )
        if project is None:
            raise ProjectNotFoundException()
        if name is not None:
            asset.name = name
        if asset_type is not None:
            asset.asset_type = asset_type
        if ip_address is not None:
            asset.ip_address = ip_address
        updated_asset = await self._repository.update(
            asset
        )
        await self._session.commit()
        return updated_asset
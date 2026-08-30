from ipaddress import ip_address
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ProjectNotFoundException
from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository
from app.repositories.project_repository import ProjectRepository


class AssetService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = AssetRepository(session)
        self._project_repository = ProjectRepository(session)

    async def _get_owned_asset(self, asset_id: UUID, owner_id: UUID) -> Asset:
        asset = await self._repository.get_by_id(asset_id)
        if asset is None:
            raise ProjectNotFoundException()
        project = await self._project_repository.get_by_id_and_owner(asset.project_id, owner_id)
        if project is None:
            raise ProjectNotFoundException()
        return asset

    @staticmethod
    def _validate_asset(name: str, asset_type: str, ip_address_value: str | None) -> tuple[str, str, str | None]:
        normalized_name = name.strip()
        normalized_type = asset_type.strip().lower()
        if not normalized_name:
            raise BadRequestException("Asset name must not be empty")
        if not normalized_type:
            raise BadRequestException("Asset type must not be empty")
        normalized_ip = ip_address_value.strip() if ip_address_value else None
        if normalized_ip:
            try:
                ip_address(normalized_ip)
            except ValueError as exc:
                raise BadRequestException("Invalid IP address") from exc
        return normalized_name, normalized_type, normalized_ip

    async def create_asset(self, project_id: UUID, name: str, asset_type: str, ip_address: str | None = None) -> Asset:
        name, asset_type, ip_address = self._validate_asset(name, asset_type, ip_address)
        asset = Asset(project_id=project_id, name=name, asset_type=asset_type, ip_address=ip_address)
        created_asset = await self._repository.create(asset)
        await self._session.commit()
        return created_asset

    async def list_assets(self, project_id: UUID):
        return await self._repository.get_by_project(project_id)

    async def delete_asset(self, asset_id: UUID, owner_id: UUID) -> None:
        asset = await self._get_owned_asset(asset_id, owner_id)
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
        asset = await self._get_owned_asset(asset_id, owner_id)
        if name is not None:
            asset.name = name.strip()
            if not asset.name:
                raise BadRequestException("Asset name must not be empty")
        if asset_type is not None:
            asset.asset_type = asset_type.strip().lower()
            if not asset.asset_type:
                raise BadRequestException("Asset type must not be empty")
        if ip_address is not None:
            normalized_ip = ip_address.strip()
            if normalized_ip:
                try:
                    ip_address(normalized_ip)
                except ValueError as exc:
                    raise BadRequestException("Invalid IP address") from exc
            asset.ip_address = normalized_ip or None
        updated_asset = await self._repository.update(asset)
        await self._session.commit()
        return updated_asset

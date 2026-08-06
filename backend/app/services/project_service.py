from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ProjectNotFoundException
from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._project_repository = ProjectRepository(session)

    async def create_project(
        self,
        owner: User,
        name: str,
        description: str | None,
    ) -> Project:

        project = Project(
            owner_id=owner.id,
            name=name,
            description=description,
        )

        created_project = await self._project_repository.create(project)

        await self._session.commit()

        return created_project

    async def get_my_projects(
        self,
        owner: User,
    ) -> list[Project]:

        return await self._project_repository.get_all_by_owner(
            owner.id
        )

    async def get_project(
        self,
        project_id: UUID,
    ) -> Project:

        project = await self._project_repository.get_by_id(
            project_id
        )

        if project is None:
            raise ProjectNotFoundException()

        return project
from uuid import UUID

from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectRead
from app.security.dependencies import get_current_user
from app.services.project_service import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "",
    response_model=ProjectRead,
)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):

    service = ProjectService(db)

    return await service.create_project(
        owner=current_user,
        name=data.name,
        description=data.description,
    )


@router.get(
    "",
    response_model=list[ProjectRead],
)
async def list_projects(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):

    service = ProjectService(db)

    return await service.get_my_projects(current_user)


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):

    service = ProjectService(db)

    return await service.get_project(project_id)
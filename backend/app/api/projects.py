from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectResponse, ProjectUpdate
from app.schemas.error import ERROR_RESPONSES

router = APIRouter(tags=["Projects"])


@router.get(
    "/",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List all projects",
    description="Retrieves a list of all canvas projects saved by the current authenticated user, ordered by the most recently updated.",
    responses={
        200: {"description": "Projects retrieved successfully"},
        401: ERROR_RESPONSES[401],
        500: ERROR_RESPONSES[500],
    }
)
async def list_projects(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """List all saved projects for the current user."""
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(desc(Project.updated_at))
    )
    return result.scalars().all()


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Saves a new project along with its initial canvas state and layout properties.",
    responses={
        201: {"description": "Project created successfully"},
        400: ERROR_RESPONSES[400],
        401: ERROR_RESPONSES[401],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    }
)
async def create_project(
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a new project with its canvas state."""
    db_project = Project(
        user_id=current_user.id,
        title=project_in.title or "Untitled Design",
        status=project_in.status or "draft",
        canvas_state=project_in.canvas_state,
        aspect_ratio=project_in.aspect_ratio or "1:1",
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project details",
    description="Retrieves the full details and canvas state of a specific project owned by the current user.",
    responses={
        200: {"description": "Project retrieved successfully"},
        401: ERROR_RESPONSES[401],
        404: ERROR_RESPONSES[404],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    }
)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific project."""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id, Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a project",
    description="Updates an existing project's canvas state, title, status, or aspect ratio.",
    responses={
        200: {"description": "Project updated successfully"},
        400: ERROR_RESPONSES[400],
        401: ERROR_RESPONSES[401],
        404: ERROR_RESPONSES[404],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    }
)
async def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing project's canvas state, title, or status."""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id, Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_in.title is not None:
        project.title = project_in.title
    if project_in.status is not None:
        project.status = project_in.status
    if project_in.canvas_state is not None:
        project.canvas_state = project_in.canvas_state
    if project_in.aspect_ratio is not None:
        project.aspect_ratio = project_in.aspect_ratio

    await db.commit()
    await db.refresh(project)
    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    description="Permanently deletes a saved project.",
    responses={
        204: {"description": "Project deleted successfully"},
        401: ERROR_RESPONSES[401],
        404: ERROR_RESPONSES[404],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    }
)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a saved project."""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id, Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.delete(project)
    await db.commit()
    return None

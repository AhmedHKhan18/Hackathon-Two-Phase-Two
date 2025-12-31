"""Task CRUD endpoints."""

from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from auth import get_current_user
from models import Task, TaskCreate, TaskUpdate, TaskResponse, DeleteResponse

router = APIRouter()


def verify_user_access(user_id: str, current_user: Dict[str, Any]) -> None:
    """
    Verify that the route user_id matches the authenticated user.

    Args:
        user_id: User ID from route parameter
        current_user: Authenticated user from JWT

    Raises:
        HTTPException: 403 if user_id doesn't match
    """
    if user_id != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Cannot access other users' tasks"
        )


@router.get("/{user_id}/tasks", response_model=List[TaskResponse])
def list_tasks(
    user_id: str,
    session: Session = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Task]:
    """
    List all tasks for the authenticated user.

    Args:
        user_id: User ID from route (must match JWT)
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        List of tasks belonging to the user
    """
    verify_user_access(user_id, current_user)

    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return list(tasks)


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    user_id: str,
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Task:
    """
    Create a new task for the authenticated user.

    Args:
        user_id: User ID from route (must match JWT)
        task_data: Task creation data (title required, description optional)
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        Created task
    """
    verify_user_access(user_id, current_user)

    # Validate title
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required"
        )

    if len(task_data.title) > 200:
        raise HTTPException(
            status_code=400,
            detail="Title must be 200 characters or less"
        )

    if task_data.description and len(task_data.description) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Description must be 2000 characters or less"
        )

    # Create task with user_id from JWT (not from request body)
    task = Task(
        user_id=current_user["id"],
        title=task_data.title.strip(),
        description=task_data.description.strip() if task_data.description else None,
        completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Task:
    """
    Get a single task by ID.

    Args:
        user_id: User ID from route (must match JWT)
        task_id: Task ID
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        Task if found

    Raises:
        HTTPException: 404 if task not found (prevents user enumeration)
    """
    verify_user_access(user_id, current_user)

    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Task:
    """
    Update an existing task.

    Args:
        user_id: User ID from route (must match JWT)
        task_id: Task ID
        task_data: Fields to update
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        Updated task
    """
    verify_user_access(user_id, current_user)

    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Update fields if provided
    if task_data.title is not None:
        if not task_data.title.strip():
            raise HTTPException(
                status_code=400,
                detail="Title is required"
            )
        if len(task_data.title) > 200:
            raise HTTPException(
                status_code=400,
                detail="Title must be 200 characters or less"
            )
        task.title = task_data.title.strip()

    if task_data.description is not None:
        if len(task_data.description) > 2000:
            raise HTTPException(
                status_code=400,
                detail="Description must be 2000 characters or less"
            )
        task.description = task_data.description.strip() if task_data.description else None

    if task_data.completed is not None:
        task.completed = task_data.completed

    task.updated_at = datetime.now(timezone.utc)

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/{user_id}/tasks/{task_id}", response_model=DeleteResponse)
def delete_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> DeleteResponse:
    """
    Delete a task.

    Args:
        user_id: User ID from route (must match JWT)
        task_id: Task ID
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        Delete confirmation
    """
    verify_user_access(user_id, current_user)

    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    session.delete(task)
    session.commit()

    return DeleteResponse(deleted=True)


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
def toggle_task_complete(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Task:
    """
    Toggle task completion status.

    Args:
        user_id: User ID from route (must match JWT)
        task_id: Task ID
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        Updated task with toggled completion status
    """
    verify_user_access(user_id, current_user)

    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)

    session.add(task)
    session.commit()
    session.refresh(task)

    return task

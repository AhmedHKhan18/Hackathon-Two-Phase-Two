"""MCP Tools for task management operations.

These tools are exposed to the AI agent for natural language task management.
All tools enforce user isolation by requiring and using user_id in queries.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select

import sys
sys.path.insert(0, '..')

from database import engine
from models import Task


def add_task(user_id: str, title: str, description: Optional[str] = None) -> dict:
    """Create a new task for the specified user.

    Args:
        user_id: The user ID who owns this task (required)
        title: Task title (required, max 200 characters)
        description: Task description (optional, max 2000 characters)

    Returns:
        Dict with status, task_id, title, and message
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        return {"status": "error", "error": "User ID is required"}

    if not title or not title.strip():
        return {"status": "error", "error": "Title is required"}

    title = title.strip()
    if len(title) > 200:
        return {"status": "error", "error": "Title must be 200 characters or less"}

    if description:
        description = description.strip()
        if len(description) > 2000:
            return {"status": "error", "error": "Description must be 2000 characters or less"}

    try:
        with Session(engine) as session:
            task = Task(
                user_id=user_id,
                title=title,
                description=description if description else None,
                completed=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "success",
                "task_id": task.id,
                "title": task.title,
                "message": "Task created successfully"
            }
    except Exception as e:
        return {"status": "error", "error": "Failed to create task"}


def list_tasks(user_id: str, status: str = "all") -> dict:
    """Retrieve tasks for the specified user with optional filtering.

    Args:
        user_id: The user ID whose tasks to retrieve (required)
        status: Filter by completion status - "all", "pending", or "completed"

    Returns:
        Dict with status, count, and tasks array
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        return {"status": "error", "error": "User ID is required"}

    if status not in ["all", "pending", "completed"]:
        return {"status": "error", "error": "Invalid status filter. Use 'all', 'pending', or 'completed'"}

    try:
        with Session(engine) as session:
            # Build query with user isolation
            query = select(Task).where(Task.user_id == user_id)

            # Apply status filter
            if status == "pending":
                query = query.where(Task.completed == False)
            elif status == "completed":
                query = query.where(Task.completed == True)

            # Order by created_at descending (newest first)
            query = query.order_by(Task.created_at.desc())

            tasks = session.exec(query).all()

            task_list = [
                {
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ]

            result = {
                "status": "success",
                "count": len(task_list),
                "tasks": task_list
            }

            if len(task_list) == 0:
                result["message"] = "No tasks found"

            return result
    except Exception as e:
        return {"status": "error", "error": "Failed to retrieve tasks"}


def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a specific task as completed.

    Args:
        user_id: The user ID who owns this task (required)
        task_id: The ID of the task to complete (required)

    Returns:
        Dict with status, task_id, title, completed, and message
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        return {"status": "error", "error": "User ID is required"}

    if not isinstance(task_id, int) or task_id <= 0:
        return {"status": "error", "error": "Invalid task ID"}

    try:
        with Session(engine) as session:
            # Query with user isolation to prevent accessing other users' tasks
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()

            if not task:
                return {"status": "error", "error": "Task not found", "task_id": task_id}

            task.completed = True
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "success",
                "task_id": task.id,
                "title": task.title,
                "completed": True,
                "message": "Task marked as complete"
            }
    except Exception as e:
        return {"status": "error", "error": "Failed to complete task"}


def delete_task(user_id: str, task_id: int) -> dict:
    """Permanently remove a task.

    Args:
        user_id: The user ID who owns this task (required)
        task_id: The ID of the task to delete (required)

    Returns:
        Dict with status, task_id, title, and message
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        return {"status": "error", "error": "User ID is required"}

    if not isinstance(task_id, int) or task_id <= 0:
        return {"status": "error", "error": "Invalid task ID"}

    try:
        with Session(engine) as session:
            # Query with user isolation
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()

            if not task:
                return {"status": "error", "error": "Task not found", "task_id": task_id}

            # Store title before deletion for response
            title = task.title

            session.delete(task)
            session.commit()

            return {
                "status": "success",
                "task_id": task_id,
                "title": title,
                "message": "Task deleted successfully"
            }
    except Exception as e:
        return {"status": "error", "error": "Failed to delete task"}


def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """Modify task title and/or description.

    Args:
        user_id: The user ID who owns this task (required)
        task_id: The ID of the task to update (required)
        title: New task title (optional, max 200 characters)
        description: New task description (optional, max 2000 characters)

    Returns:
        Dict with status, task_id, title, description, and message
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        return {"status": "error", "error": "User ID is required"}

    if not isinstance(task_id, int) or task_id <= 0:
        return {"status": "error", "error": "Invalid task ID"}

    # At least one field must be provided
    if title is None and description is None:
        return {"status": "error", "error": "No fields provided to update"}

    # Validate title if provided
    if title is not None:
        title = title.strip()
        if not title:
            return {"status": "error", "error": "Title cannot be empty"}
        if len(title) > 200:
            return {"status": "error", "error": "Title must be 200 characters or less"}

    # Validate description if provided
    if description is not None:
        description = description.strip()
        if len(description) > 2000:
            return {"status": "error", "error": "Description must be 2000 characters or less"}

    try:
        with Session(engine) as session:
            # Query with user isolation
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()

            if not task:
                return {"status": "error", "error": "Task not found", "task_id": task_id}

            # Update provided fields only
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description if description else None

            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "success",
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "message": "Task updated successfully"
            }
    except Exception as e:
        return {"status": "error", "error": "Failed to update task"}


# Tool metadata for agent registration
TOOL_DEFINITIONS = [
    {
        "name": "add_task",
        "description": "Create a new task with a title and optional description",
        "function": add_task,
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user ID who owns this task (required)"
                },
                "title": {
                    "type": "string",
                    "description": "Task title (required, max 200 characters)"
                },
                "description": {
                    "type": "string",
                    "description": "Task description (optional, max 2000 characters)"
                }
            },
            "required": ["user_id", "title"]
        }
    },
    {
        "name": "list_tasks",
        "description": "Get all tasks or filter by pending/completed status",
        "function": list_tasks,
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user ID whose tasks to retrieve (required)"
                },
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter by completion status (optional, defaults to 'all')"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a specific task as completed",
        "function": complete_task,
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user ID who owns this task (required)"
                },
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to complete (required)"
                }
            },
            "required": ["user_id", "task_id"]
        }
    },
    {
        "name": "delete_task",
        "description": "Permanently remove a task",
        "function": delete_task,
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user ID who owns this task (required)"
                },
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to delete (required)"
                }
            },
            "required": ["user_id", "task_id"]
        }
    },
    {
        "name": "update_task",
        "description": "Change a task's title or description",
        "function": update_task,
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user ID who owns this task (required)"
                },
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to update (required)"
                },
                "title": {
                    "type": "string",
                    "description": "New task title (optional, max 200 characters)"
                },
                "description": {
                    "type": "string",
                    "description": "New task description (optional, max 2000 characters)"
                }
            },
            "required": ["user_id", "task_id"]
        }
    }
]

"""CRUD endpoints and basic task statistics."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Task, TaskPriority, TaskStatus
from app.schemas import TaskCreate, TaskPage, TaskRead, TaskStats, TaskUpdate

router = APIRouter(prefix="/api/v1", tags=["tasks"])
DbSession = Annotated[Session, Depends(get_db)]


def find_task(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: DbSession) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks", response_model=TaskPage)
def list_tasks(
    db: DbSession,
    task_status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    priority: TaskPriority | None = None,
    search: Annotated[str | None, Query(max_length=120)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> TaskPage:
    query = select(Task)
    if task_status is not None:
        query = query.where(Task.status == task_status)
    if priority is not None:
        query = query.where(Task.priority == priority)
    if search:
        query = query.where(Task.title.ilike(f"%{search}%"))

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(query.order_by(Task.id.desc()).offset(offset).limit(limit)).all()
    return TaskPage(items=items, total=total, offset=offset, limit=limit)


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: DbSession) -> Task:
    return find_task(db, task_id)


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, db: DbSession) -> Task:
    task = find_task(db, task_id)
    update_data = payload.model_dump(exclude_unset=True)
    for field in ("title", "status", "priority"):
        if field in update_data and update_data[field] is None:
            raise HTTPException(status_code=422, detail=f"{field} cannot be null")
    for field, value in update_data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: DbSession) -> Response:
    task = find_task(db, task_id)
    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/stats", response_model=TaskStats, tags=["statistics"])
def task_stats(db: DbSession) -> TaskStats:
    counts = {value.value: 0 for value in TaskStatus}
    rows = db.execute(select(Task.status, func.count(Task.id)).group_by(Task.status))
    for task_status, count in rows:
        counts[task_status.value] = count
    return TaskStats(total=sum(counts.values()), by_status=counts)

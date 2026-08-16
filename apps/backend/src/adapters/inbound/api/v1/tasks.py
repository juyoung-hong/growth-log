from fastapi import APIRouter, Depends, HTTPException

from adapters.inbound.api.deps import get_task_comment_service, get_task_service
from adapters.inbound.api.schemas.task import (
    TaskActivityLogRead,
    TaskCreate,
    TaskRead,
    TaskScheduleUpdate,
    TaskStatusUpdate,
    TaskUpdate,
)
from adapters.inbound.api.schemas.task_comment import (
    TaskCommentCreate,
    TaskCommentRead,
    TaskCommentUpdate,
)
from application.services.task_comment_service import TaskCommentService
from application.services.task_service import TaskService
from domain.common.exceptions import InvalidFieldError
from domain.exceptions import (
    TaskCommentNotFoundError,
    TaskGroupNotFoundError,
    TaskNotFoundError,
)

router = APIRouter(tags=["tasks"])


@router.get("/task-groups/{task_group_id}/tasks", response_model=list[TaskRead])
def list_tasks(
    task_group_id: int,
    view: str = "default",
    service: TaskService = Depends(get_task_service),
):
    try:
        return service.list(task_group_id, view=view)
    except TaskGroupNotFoundError:
        raise HTTPException(status_code=404, detail="TaskGroup을 찾을 수 없습니다.")


@router.post(
    "/task-groups/{task_group_id}/tasks", response_model=TaskRead, status_code=201
)
def create_task(
    task_group_id: int,
    body: TaskCreate,
    service: TaskService = Depends(get_task_service),
):
    try:
        return service.create(task_group_id=task_group_id, **body.model_dump())
    except TaskGroupNotFoundError:
        raise HTTPException(status_code=404, detail="TaskGroup을 찾을 수 없습니다.")
    except InvalidFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    try:
        return service.get(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int, body: TaskUpdate, service: TaskService = Depends(get_task_service)
):
    try:
        return service.update(task_id, **body.model_dump(exclude_unset=True))
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")
    except InvalidFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/tasks/{task_id}/status", response_model=TaskRead)
def update_task_status(
    task_id: int,
    body: TaskStatusUpdate,
    service: TaskService = Depends(get_task_service),
):
    try:
        return service.change_status(task_id, body.status)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")


@router.patch("/tasks/{task_id}/schedule", response_model=TaskRead)
def update_task_schedule(
    task_id: int,
    body: TaskScheduleUpdate,
    service: TaskService = Depends(get_task_service),
):
    try:
        return service.change_schedule(
            task_id, body.start_date, body.due_date, body.reason
        )
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")
    except InvalidFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    try:
        service.delete(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")


@router.get("/tasks/{task_id}/activity-log", response_model=list[TaskActivityLogRead])
def list_activity_log(task_id: int, service: TaskService = Depends(get_task_service)):
    try:
        return service.list_activity_log(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")


@router.get("/tasks/{task_id}/comments", response_model=list[TaskCommentRead])
def list_comments(
    task_id: int, service: TaskCommentService = Depends(get_task_comment_service)
):
    try:
        return service.list(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")


@router.post(
    "/tasks/{task_id}/comments", response_model=TaskCommentRead, status_code=201
)
def create_comment(
    task_id: int,
    body: TaskCommentCreate,
    service: TaskCommentService = Depends(get_task_comment_service),
):
    try:
        return service.create(task_id, body.content)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")
    except InvalidFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/comments/{comment_id}", response_model=TaskCommentRead)
def update_comment(
    comment_id: int,
    body: TaskCommentUpdate,
    service: TaskCommentService = Depends(get_task_comment_service),
):
    try:
        return service.update(comment_id, body.content)
    except TaskCommentNotFoundError:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    except InvalidFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    service: TaskCommentService = Depends(get_task_comment_service),
):
    try:
        service.delete(comment_id)
    except TaskCommentNotFoundError:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

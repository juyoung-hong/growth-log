from fastapi import APIRouter, Depends, HTTPException

from adapters.inbound.api.deps import get_task_group_service
from adapters.inbound.api.schemas.task_group import (
    TaskGroupCreate,
    TaskGroupRead,
    TaskGroupUpdate,
)
from application.services.task_group_service import TaskGroupService
from domain.common.enums import Scope, TaskStatus
from domain.common.exceptions import InvalidFieldError
from domain.exceptions import TaskGroupNotFoundError

router = APIRouter(prefix="/task-groups", tags=["task-groups"])


@router.get("", response_model=list[TaskGroupRead])
def list_task_groups(
    category: Scope | None = None,
    status: TaskStatus | None = None,
    include_archived: bool = False,
    service: TaskGroupService = Depends(get_task_group_service),
):
    return service.list(category, status, include_archived)


@router.post("", response_model=TaskGroupRead, status_code=201)
def create_task_group(
    body: TaskGroupCreate, service: TaskGroupService = Depends(get_task_group_service)
):
    try:
        return service.create(**body.model_dump())
    except InvalidFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_group_id}", response_model=TaskGroupRead)
def get_task_group(
    task_group_id: int, service: TaskGroupService = Depends(get_task_group_service)
):
    try:
        return service.get(task_group_id)
    except TaskGroupNotFoundError:
        raise HTTPException(status_code=404, detail="작업 그룹을 찾을 수 없습니다.")


@router.patch("/{task_group_id}", response_model=TaskGroupRead)
def update_task_group(
    task_group_id: int,
    body: TaskGroupUpdate,
    service: TaskGroupService = Depends(get_task_group_service),
):
    try:
        return service.update(task_group_id, **body.model_dump(exclude_unset=True))
    except TaskGroupNotFoundError:
        raise HTTPException(status_code=404, detail="작업 그룹을 찾을 수 없습니다.")
    except InvalidFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{task_group_id}", status_code=204)
def delete_task_group(
    task_group_id: int, service: TaskGroupService = Depends(get_task_group_service)
):
    try:
        service.delete(task_group_id)
    except TaskGroupNotFoundError:
        raise HTTPException(status_code=404, detail="작업 그룹을 찾을 수 없습니다.")

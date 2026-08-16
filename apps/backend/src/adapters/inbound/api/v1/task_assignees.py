from fastapi import APIRouter, Depends, HTTPException

from adapters.inbound.api.deps import get_task_assignee_service
from adapters.inbound.api.schemas.person import PersonRead
from adapters.inbound.api.schemas.task_assignee import TaskAssigneeAdd
from application.services.task_assignee_service import TaskAssigneeService
from domain.exceptions import PersonNotFoundError, TaskNotFoundError

router = APIRouter(tags=["task-assignees"])


@router.get("/tasks/{task_id}/assignees", response_model=list[PersonRead])
def list_assignees(
    task_id: int, service: TaskAssigneeService = Depends(get_task_assignee_service)
):
    try:
        return service.list(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")


@router.post("/tasks/{task_id}/assignees", response_model=PersonRead, status_code=201)
def add_assignee(
    task_id: int,
    body: TaskAssigneeAdd,
    service: TaskAssigneeService = Depends(get_task_assignee_service),
):
    try:
        return service.add(task_id, body.person_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")
    except PersonNotFoundError:
        raise HTTPException(status_code=404, detail="인물을 찾을 수 없습니다.")


@router.delete("/tasks/{task_id}/assignees/{person_id}", status_code=204)
def remove_assignee(
    task_id: int,
    person_id: int,
    service: TaskAssigneeService = Depends(get_task_assignee_service),
):
    try:
        service.remove(task_id, person_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")
    except PersonNotFoundError:
        raise HTTPException(status_code=404, detail="인물을 찾을 수 없습니다.")

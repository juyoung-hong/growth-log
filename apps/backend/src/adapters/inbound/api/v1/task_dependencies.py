from fastapi import APIRouter, Depends, HTTPException

from adapters.inbound.api.deps import get_task_dependency_service
from adapters.inbound.api.schemas.task import TaskRead
from adapters.inbound.api.schemas.task_dependency import TaskDependencyAdd
from application.services.task_dependency_service import TaskDependencyService
from domain.common.exceptions import InvalidFieldError
from domain.exceptions import DependencyTaskGroupMismatchError, TaskNotFoundError

router = APIRouter(tags=["task-dependencies"])


@router.get("/tasks/{task_id}/dependencies", response_model=list[TaskRead])
def list_dependencies(
    task_id: int,
    service: TaskDependencyService = Depends(get_task_dependency_service),
):
    try:
        return service.list(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")


@router.post("/tasks/{task_id}/dependencies", response_model=TaskRead, status_code=201)
def add_dependency(
    task_id: int,
    body: TaskDependencyAdd,
    service: TaskDependencyService = Depends(get_task_dependency_service),
):
    try:
        return service.add(task_id, body.depends_on_task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")
    except InvalidFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DependencyTaskGroupMismatchError:
        raise HTTPException(
            status_code=422, detail="선행 태스크는 같은 TaskGroup에 속해야 합니다."
        )


@router.delete("/tasks/{task_id}/dependencies/{depends_on_task_id}", status_code=204)
def remove_dependency(
    task_id: int,
    depends_on_task_id: int,
    service: TaskDependencyService = Depends(get_task_dependency_service),
):
    try:
        service.remove(task_id, depends_on_task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")

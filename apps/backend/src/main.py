from fastapi import FastAPI

from adapters.inbound.api.v1.holidays import router as holidays_router
from adapters.inbound.api.v1.meetings import router as meetings_router
from adapters.inbound.api.v1.persons import router as persons_router
from adapters.inbound.api.v1.storage import router as storage_router
from adapters.inbound.api.v1.task_assignees import router as task_assignees_router
from adapters.inbound.api.v1.task_dependencies import router as task_dependencies_router
from adapters.inbound.api.v1.task_group_attachments import (
    router as task_group_attachments_router,
)
from adapters.inbound.api.v1.task_groups import router as task_groups_router
from adapters.inbound.api.v1.tasks import router as tasks_router

app = FastAPI(title="Growth Log API")

app.include_router(persons_router, prefix="/api/v1")
app.include_router(task_groups_router, prefix="/api/v1")
app.include_router(task_group_attachments_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(task_assignees_router, prefix="/api/v1")
app.include_router(task_dependencies_router, prefix="/api/v1")
app.include_router(meetings_router, prefix="/api/v1")
app.include_router(storage_router, prefix="/api/v1")
app.include_router(holidays_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

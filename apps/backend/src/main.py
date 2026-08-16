from fastapi import FastAPI

from adapters.inbound.api.v1.persons import router as persons_router
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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

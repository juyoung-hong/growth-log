from pydantic import BaseModel


class TaskDependencyAdd(BaseModel):
    depends_on_task_id: int

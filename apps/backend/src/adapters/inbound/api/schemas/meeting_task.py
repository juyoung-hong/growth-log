from pydantic import BaseModel


class MeetingTaskAdd(BaseModel):
    task_id: int

from pydantic import BaseModel


class TaskAssigneeAdd(BaseModel):
    person_id: int

from pydantic import BaseModel


class MeetingAttendeeAdd(BaseModel):
    person_id: int

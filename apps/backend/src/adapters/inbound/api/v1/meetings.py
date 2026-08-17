"""미팅 라우터."""

from fastapi import APIRouter, Depends, HTTPException

from adapters.inbound.api.deps import (
    get_meeting_attendee_service,
    get_meeting_service,
    get_meeting_task_service,
)
from adapters.inbound.api.schemas.meeting import (
    MeetingCreate,
    MeetingRead,
    MeetingUpdate,
)
from adapters.inbound.api.schemas.meeting_attendee import MeetingAttendeeAdd
from adapters.inbound.api.schemas.meeting_task import MeetingTaskAdd
from adapters.inbound.api.schemas.person import PersonRead
from adapters.inbound.api.schemas.task import TaskRead
from application.services.meeting_attendee_service import MeetingAttendeeService
from application.services.meeting_service import MeetingService
from application.services.meeting_task_service import MeetingTaskService
from domain.exceptions import (
    MeetingNotFoundError,
    PersonNotFoundError,
    TaskGroupNotFoundError,
    TaskNotFoundError,
)
from domain.meeting import Meeting

router = APIRouter(tags=["meetings"])


def build_meeting_read(
    meeting: Meeting,
    attendee_service: MeetingAttendeeService,
    task_link_service: MeetingTaskService,
) -> MeetingRead:
    """Meeting 도메인 객체에 참석자·연결 태스크를 채워서 응답 스키마로 조립한다."""
    return MeetingRead(
        id=meeting.id,
        task_group_id=meeting.task_group_id,
        status=meeting.status,
        scheduled_at=meeting.scheduled_at,
        agenda=meeting.agenda,
        content=meeting.content,
        attendees=[
            PersonRead.model_validate(p, from_attributes=True)
            for p in attendee_service.list(meeting.id)
        ],
        tasks=[
            TaskRead.model_validate(t, from_attributes=True)
            for t in task_link_service.list(meeting.id)
        ],
    )


@router.get("/task-groups/{task_group_id}/meetings", response_model=list[MeetingRead])
def list_meetings(
    task_group_id: int,
    service: MeetingService = Depends(get_meeting_service),
    attendee_service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
    task_link_service: MeetingTaskService = Depends(get_meeting_task_service),
):
    try:
        meetings = service.list(task_group_id)
    except TaskGroupNotFoundError:
        raise HTTPException(status_code=404, detail="TaskGroup을 찾을 수 없습니다.")
    return [
        build_meeting_read(m, attendee_service, task_link_service) for m in meetings
    ]


@router.post(
    "/task-groups/{task_group_id}/meetings", response_model=MeetingRead, status_code=201
)
def create_meeting(
    task_group_id: int,
    body: MeetingCreate,
    service: MeetingService = Depends(get_meeting_service),
    attendee_service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
    task_link_service: MeetingTaskService = Depends(get_meeting_task_service),
):
    try:
        meeting = service.create(task_group_id, body.scheduled_at, body.agenda)
    except TaskGroupNotFoundError:
        raise HTTPException(status_code=404, detail="TaskGroup을 찾을 수 없습니다.")

    try:
        for person_id in body.attendee_person_ids:
            attendee_service.add(meeting.id, person_id)
        for task_id in body.task_ids:
            task_link_service.add(meeting.id, task_id)
    except PersonNotFoundError:
        raise HTTPException(status_code=404, detail="인물을 찾을 수 없습니다.")
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")

    return build_meeting_read(meeting, attendee_service, task_link_service)


@router.get("/meetings/{meeting_id}", response_model=MeetingRead)
def get_meeting(
    meeting_id: int,
    service: MeetingService = Depends(get_meeting_service),
    attendee_service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
    task_link_service: MeetingTaskService = Depends(get_meeting_task_service),
):
    try:
        meeting = service.get(meeting_id)
    except MeetingNotFoundError:
        raise HTTPException(status_code=404, detail="미팅을 찾을 수 없습니다.")
    return build_meeting_read(meeting, attendee_service, task_link_service)


@router.patch("/meetings/{meeting_id}", response_model=MeetingRead)
def update_meeting(
    meeting_id: int,
    body: MeetingUpdate,
    service: MeetingService = Depends(get_meeting_service),
    attendee_service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
    task_link_service: MeetingTaskService = Depends(get_meeting_task_service),
):
    try:
        meeting = service.update(meeting_id, **body.model_dump(exclude_unset=True))
    except MeetingNotFoundError:
        raise HTTPException(status_code=404, detail="미팅을 찾을 수 없습니다.")
    return build_meeting_read(meeting, attendee_service, task_link_service)


@router.delete("/meetings/{meeting_id}", status_code=204)
def delete_meeting(
    meeting_id: int, service: MeetingService = Depends(get_meeting_service)
):
    try:
        service.delete(meeting_id)
    except MeetingNotFoundError:
        raise HTTPException(status_code=404, detail="미팅을 찾을 수 없습니다.")


@router.post(
    "/meetings/{meeting_id}/attendees", response_model=PersonRead, status_code=201
)
def add_meeting_attendee(
    meeting_id: int,
    body: MeetingAttendeeAdd,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
):
    try:
        return service.add(meeting_id, body.person_id)
    except MeetingNotFoundError:
        raise HTTPException(status_code=404, detail="미팅을 찾을 수 없습니다.")
    except PersonNotFoundError:
        raise HTTPException(status_code=404, detail="인물을 찾을 수 없습니다.")


@router.delete("/meetings/{meeting_id}/attendees/{person_id}", status_code=204)
def remove_meeting_attendee(
    meeting_id: int,
    person_id: int,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
):
    try:
        service.remove(meeting_id, person_id)
    except MeetingNotFoundError:
        raise HTTPException(status_code=404, detail="미팅을 찾을 수 없습니다.")


@router.post("/meetings/{meeting_id}/tasks", response_model=TaskRead, status_code=201)
def add_meeting_task(
    meeting_id: int,
    body: MeetingTaskAdd,
    service: MeetingTaskService = Depends(get_meeting_task_service),
):
    try:
        return service.add(meeting_id, body.task_id)
    except MeetingNotFoundError:
        raise HTTPException(status_code=404, detail="미팅을 찾을 수 없습니다.")
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task를 찾을 수 없습니다.")


@router.delete("/meetings/{meeting_id}/tasks/{task_id}", status_code=204)
def remove_meeting_task(
    meeting_id: int,
    task_id: int,
    service: MeetingTaskService = Depends(get_meeting_task_service),
):
    try:
        service.remove(meeting_id, task_id)
    except MeetingNotFoundError:
        raise HTTPException(status_code=404, detail="미팅을 찾을 수 없습니다.")

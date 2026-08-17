"""MeetingAttendeeService 유스케이스를 Fake로 DB 없이 검증한다."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from application.services.meeting_attendee_service import MeetingAttendeeService
from application.services.meeting_service import MeetingService
from domain.common.enums import Scope
from domain.exceptions import MeetingNotFoundError, PersonNotFoundError
from domain.person import Person
from domain.task_group import TaskGroup


def test_참석자를_추가한다(
    meeting_attendee_service: MeetingAttendeeService,
    meeting_service: MeetingService,
    task_group_repository,
    person_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    meeting = meeting_service.create(
        task_group_id=task_group.id,
        scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
    )
    person = person_repository.add(
        Person(id=None, category=Scope.COMPANY, name="홍주영")
    )

    added = meeting_attendee_service.add(meeting.id, person.id)

    assert added.id == person.id
    assert [p.name for p in meeting_attendee_service.list(meeting.id)] == ["홍주영"]


def test_같은_참석자를_두번_추가해도_멱등하다(
    meeting_attendee_service: MeetingAttendeeService,
    meeting_service: MeetingService,
    task_group_repository,
    person_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    meeting = meeting_service.create(
        task_group_id=task_group.id,
        scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
    )
    person = person_repository.add(
        Person(id=None, category=Scope.COMPANY, name="홍주영")
    )

    meeting_attendee_service.add(meeting.id, person.id)
    meeting_attendee_service.add(meeting.id, person.id)

    assert len(meeting_attendee_service.list(meeting.id)) == 1


def test_없는_미팅에_참석자를_추가하면_예외(
    meeting_attendee_service: MeetingAttendeeService, person_repository
) -> None:
    person = person_repository.add(
        Person(id=None, category=Scope.COMPANY, name="홍주영")
    )
    with pytest.raises(MeetingNotFoundError):
        meeting_attendee_service.add(999, person.id)


def test_없는_인물을_참석자로_추가하면_예외(
    meeting_attendee_service: MeetingAttendeeService,
    meeting_service: MeetingService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    meeting = meeting_service.create(
        task_group_id=task_group.id,
        scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
    )
    with pytest.raises(PersonNotFoundError):
        meeting_attendee_service.add(meeting.id, 999)


def test_참석자를_제거한다(
    meeting_attendee_service: MeetingAttendeeService,
    meeting_service: MeetingService,
    task_group_repository,
    person_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    meeting = meeting_service.create(
        task_group_id=task_group.id,
        scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
    )
    person = person_repository.add(
        Person(id=None, category=Scope.COMPANY, name="홍주영")
    )
    meeting_attendee_service.add(meeting.id, person.id)

    meeting_attendee_service.remove(meeting.id, person.id)

    assert meeting_attendee_service.list(meeting.id) == []

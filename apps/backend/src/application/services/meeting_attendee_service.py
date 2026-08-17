"""Meeting 참석자 유스케이스."""

from __future__ import annotations

from application.ports.outbound.meeting_attendee_repository import (
    MeetingAttendeeRepository,
)
from application.ports.outbound.meeting_repository import MeetingRepository
from application.ports.outbound.person_repository import PersonRepository
from domain.exceptions import MeetingNotFoundError, PersonNotFoundError
from domain.person import Person


class MeetingAttendeeService:
    """미팅 참석자 추가·제거·조회 유스케이스."""

    def __init__(
        self,
        attendee_repository: MeetingAttendeeRepository,
        meeting_repository: MeetingRepository,
        person_repository: PersonRepository,
    ) -> None:
        self.attendee_repository = attendee_repository
        self.meeting_repository = meeting_repository
        self.person_repository = person_repository

    def list(self, meeting_id: int) -> list[Person]:
        self._ensure_meeting_exists(meeting_id)
        person_ids = self.attendee_repository.list_person_ids(meeting_id)
        return [self.person_repository.get(pid) for pid in person_ids]

    def add(self, meeting_id: int, person_id: int) -> Person:
        """참석자를 추가하고, 추가된 인물을 반환한다. 이미 참석자면 멱등 무시
        (Task 담당자와 같은 이유 — 이슈 #9 참고)."""
        self._ensure_meeting_exists(meeting_id)
        person = self._get_person(person_id)
        if not self.attendee_repository.exists(meeting_id, person_id):
            self.attendee_repository.add(meeting_id, person_id)
        return person

    def remove(self, meeting_id: int, person_id: int) -> None:
        self._ensure_meeting_exists(meeting_id)
        self.attendee_repository.remove(meeting_id, person_id)

    def _ensure_meeting_exists(self, meeting_id: int) -> None:
        if not self.meeting_repository.get(meeting_id):
            raise MeetingNotFoundError(meeting_id)

    def _get_person(self, person_id: int) -> Person:
        person = self.person_repository.get(person_id)
        if not person:
            raise PersonNotFoundError(person_id)
        return person

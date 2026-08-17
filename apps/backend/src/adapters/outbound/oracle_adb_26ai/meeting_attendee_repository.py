from sqlmodel import Session, select

from adapters.outbound.oracle_adb_26ai.models import MeetingAttendeeTable
from application.ports.outbound.meeting_attendee_repository import (
    MeetingAttendeeRepository,
)


class SqlMeetingAttendeeRepository(MeetingAttendeeRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, meeting_id: int, person_id: int) -> None:
        row = MeetingAttendeeTable(meeting_id=meeting_id, person_id=person_id)
        self.session.add(row)
        self.session.commit()

    def remove(self, meeting_id: int, person_id: int) -> None:
        row = self.session.get(MeetingAttendeeTable, (meeting_id, person_id))
        if row:
            self.session.delete(row)
            self.session.commit()

    def exists(self, meeting_id: int, person_id: int) -> bool:
        return (
            self.session.get(MeetingAttendeeTable, (meeting_id, person_id)) is not None
        )

    def list_person_ids(self, meeting_id: int) -> list[int]:
        stmt = select(MeetingAttendeeTable.person_id).where(
            MeetingAttendeeTable.meeting_id == meeting_id
        )
        return list(self.session.exec(stmt).all())

    def delete_by_meeting(self, meeting_id: int) -> None:
        stmt = select(MeetingAttendeeTable).where(
            MeetingAttendeeTable.meeting_id == meeting_id
        )
        for row in self.session.exec(stmt).all():
            self.session.delete(row)
        self.session.commit()

    def is_person_referenced(self, person_id: int) -> bool:
        stmt = select(MeetingAttendeeTable).where(
            MeetingAttendeeTable.person_id == person_id
        )
        return self.session.exec(stmt).first() is not None

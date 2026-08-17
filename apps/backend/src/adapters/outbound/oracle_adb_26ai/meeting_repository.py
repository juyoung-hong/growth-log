from datetime import datetime, timezone

from sqlmodel import Session, select

from adapters.outbound.oracle_adb_26ai.models import MeetingTable
from application.ports.outbound.meeting_repository import MeetingRepository
from domain.meeting import Meeting, MeetingStatus


class SqlMeetingRepository(MeetingRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, meeting: Meeting) -> Meeting:
        row = MeetingTable(
            task_group_id=meeting.task_group_id,
            status=meeting.status.value,
            scheduled_at=meeting.scheduled_at,
            agenda=meeting.agenda,
            content=meeting.content,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def get(self, meeting_id: int) -> Meeting | None:
        row = self.session.get(MeetingTable, meeting_id)
        return self._to_domain(row) if row else None

    def list(self, task_group_id: int) -> list[Meeting]:
        stmt = select(MeetingTable).where(MeetingTable.task_group_id == task_group_id)
        rows = self.session.exec(stmt).all()
        return [self._to_domain(r) for r in rows]

    def update(self, meeting: Meeting) -> Meeting:
        row = self.session.get(MeetingTable, meeting.id)
        row.status = meeting.status.value
        row.scheduled_at = meeting.scheduled_at
        row.agenda = meeting.agenda
        row.content = meeting.content
        row.updated_at = datetime.now(timezone.utc)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def delete(self, meeting_id: int) -> None:
        row = self.session.get(MeetingTable, meeting_id)
        if row:
            self.session.delete(row)
            self.session.commit()

    @staticmethod
    def _to_domain(row: MeetingTable) -> Meeting:
        return Meeting(
            id=row.id,
            task_group_id=row.task_group_id,
            scheduled_at=row.scheduled_at,
            status=MeetingStatus(row.status),
            agenda=row.agenda,
            content=row.content,
        )

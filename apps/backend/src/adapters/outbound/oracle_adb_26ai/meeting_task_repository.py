from sqlmodel import Session, select

from adapters.outbound.oracle_adb_26ai.models import MeetingTaskTable
from application.ports.outbound.meeting_task_repository import MeetingTaskRepository


class SqlMeetingTaskRepository(MeetingTaskRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, meeting_id: int, task_id: int) -> None:
        row = MeetingTaskTable(meeting_id=meeting_id, task_id=task_id)
        self.session.add(row)
        self.session.commit()

    def remove(self, meeting_id: int, task_id: int) -> None:
        row = self.session.get(MeetingTaskTable, (meeting_id, task_id))
        if row:
            self.session.delete(row)
            self.session.commit()

    def exists(self, meeting_id: int, task_id: int) -> bool:
        return self.session.get(MeetingTaskTable, (meeting_id, task_id)) is not None

    def list_task_ids(self, meeting_id: int) -> list[int]:
        stmt = select(MeetingTaskTable.task_id).where(
            MeetingTaskTable.meeting_id == meeting_id
        )
        return list(self.session.exec(stmt).all())

    def list_meeting_ids_by_task(self, task_id: int) -> list[int]:
        stmt = select(MeetingTaskTable.meeting_id).where(
            MeetingTaskTable.task_id == task_id
        )
        return list(self.session.exec(stmt).all())

    def delete_by_meeting(self, meeting_id: int) -> None:
        stmt = select(MeetingTaskTable).where(MeetingTaskTable.meeting_id == meeting_id)
        for row in self.session.exec(stmt).all():
            self.session.delete(row)
        self.session.commit()

    def delete_by_task(self, task_id: int) -> None:
        stmt = select(MeetingTaskTable).where(MeetingTaskTable.task_id == task_id)
        for row in self.session.exec(stmt).all():
            self.session.delete(row)
        self.session.commit()

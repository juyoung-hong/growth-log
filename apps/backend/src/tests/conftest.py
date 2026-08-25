"""공용 pytest fixture. tests/ 하위 모든 테스트에서 바로 쓸 수 있다."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from application.ports.outbound.database_usage_port import DatabaseUsagePort
from application.ports.outbound.export_job_repository import ExportJobRepository
from application.ports.outbound.holiday_calendar_port import HolidayCalendarPort
from application.ports.outbound.meeting_attendee_repository import (
    MeetingAttendeeRepository,
)
from application.ports.outbound.meeting_repository import MeetingRepository
from application.ports.outbound.meeting_task_repository import MeetingTaskRepository
from application.ports.outbound.object_storage_port import ObjectStoragePort
from application.ports.outbound.person_repository import PersonRepository
from application.ports.outbound.storage_usage_snapshot_repository import (
    StorageUsageSnapshotRepository,
)
from application.ports.outbound.task_activity_log_repository import (
    TaskActivityLogRepository,
)
from application.ports.outbound.task_assignee_repository import TaskAssigneeRepository
from application.ports.outbound.task_comment_repository import TaskCommentRepository
from application.ports.outbound.task_dependency_repository import (
    TaskDependencyRepository,
)
from application.ports.outbound.task_group_attachment_repository import (
    TaskGroupAttachmentRepository,
)
from application.ports.outbound.task_group_repository import TaskGroupRepository
from application.ports.outbound.task_group_size_estimator import TaskGroupSizeEstimator
from application.ports.outbound.task_repository import TaskRepository
from application.services.attachment_service import AttachmentService
from application.services.export_service import ExportService
from application.services.meeting_attendee_service import MeetingAttendeeService
from application.services.meeting_service import MeetingService
from application.services.meeting_task_service import MeetingTaskService
from application.services.person_service import PersonService
from application.services.storage_service import StorageService
from application.services.task_assignee_service import TaskAssigneeService
from application.services.task_comment_service import TaskCommentService
from application.services.task_dependency_service import TaskDependencyService
from application.services.task_group_service import TaskGroupService
from application.services.task_service import TaskService
from domain.common.enums import Scope, TaskStatus
from domain.export_job import ExportJob, ExportJobTaskGroup
from domain.meeting import Meeting
from domain.person import Person
from domain.task import Task
from domain.task_activity_log import TaskActivityLog
from domain.task_comment import TaskComment
from domain.task_group import TaskGroup
from domain.task_group_attachment import TaskGroupAttachment


class FakePersonRepository(PersonRepository):
    """테스트용 인메모리 PersonRepository. 실제 DB 없이 서비스 로직만 검증한다."""

    def __init__(self) -> None:
        self._store: dict[int, Person] = {}
        self._next_id = 1
        self.referenced_ids: set[int] = set()

    def add(self, person: Person) -> Person:
        person.id = self._next_id
        self._store[person.id] = person
        self._next_id += 1
        return person

    def get(self, person_id: int) -> Person | None:
        return self._store.get(person_id)

    def list(self, category: Scope | None = None) -> list[Person]:
        values = list(self._store.values())
        if category:
            values = [p for p in values if p.category == category]
        return values

    def update(self, person: Person) -> Person:
        self._store[person.id] = person
        return person

    def delete(self, person_id: int) -> None:
        self._store.pop(person_id, None)

    def find_by_email(self, email: str) -> Person | None:
        return next((p for p in self._store.values() if p.email == email), None)

    def is_referenced(self, person_id: int) -> bool:
        return person_id in self.referenced_ids


@pytest.fixture
def person_repository() -> FakePersonRepository:
    return FakePersonRepository()


@pytest.fixture
def person_service(person_repository: FakePersonRepository) -> PersonService:
    """DB 없이 동작하는 PersonService. 매 테스트마다 빈 저장소로 새로 시작한다."""
    return PersonService(person_repository)


class FakeTaskGroupRepository(TaskGroupRepository):
    """테스트용 인메모리 TaskGroupRepository."""

    def __init__(self) -> None:
        self._store: dict[int, TaskGroup] = {}
        self._next_id = 1

    def add(self, task_group: TaskGroup) -> TaskGroup:
        task_group.id = self._next_id
        self._store[task_group.id] = task_group
        self._next_id += 1
        return task_group

    def get(self, task_group_id: int) -> TaskGroup | None:
        return self._store.get(task_group_id)

    def list(
        self,
        category: Scope | None = None,
        status: TaskStatus | None = None,
        include_archived: bool = False,
        created_after: date | None = None,
        created_before: date | None = None,
    ) -> list[TaskGroup]:
        values = list(self._store.values())
        if not include_archived:
            values = [v for v in values if not v.is_archived]
        if category:
            values = [v for v in values if v.category == category]
        if status:
            values = [v for v in values if v.status == status]
        return values

    def update(self, task_group: TaskGroup) -> TaskGroup:
        self._store[task_group.id] = task_group
        return task_group

    def delete(self, task_group_id: int) -> None:
        self._store.pop(task_group_id, None)


@pytest.fixture
def task_group_repository() -> FakeTaskGroupRepository:
    return FakeTaskGroupRepository()


@pytest.fixture
def task_group_service(
    task_group_repository: FakeTaskGroupRepository,
) -> TaskGroupService:
    """DB 없이 동작하는 TaskGroupService. 매 테스트마다 빈 저장소로 새로 시작한다."""
    return TaskGroupService(task_group_repository)


class FakeTaskGroupAttachmentRepository(TaskGroupAttachmentRepository):
    """테스트용 인메모리 TaskGroupAttachmentRepository."""

    def __init__(self) -> None:
        self._store: dict[int, TaskGroupAttachment] = {}
        self._next_id = 1

    def add(self, attachment: TaskGroupAttachment) -> TaskGroupAttachment:
        attachment.id = self._next_id
        self._store[attachment.id] = attachment
        self._next_id += 1
        return attachment

    def get(self, attachment_id: int) -> TaskGroupAttachment | None:
        return self._store.get(attachment_id)

    def list(self, task_group_id: int) -> list[TaskGroupAttachment]:
        return [a for a in self._store.values() if a.task_group_id == task_group_id]

    def delete(self, attachment_id: int) -> None:
        self._store.pop(attachment_id, None)


class FakeObjectStoragePort(ObjectStoragePort):
    """테스트용 인메모리 ObjectStoragePort. 실제 OCI 없이 업로드/삭제를 흉내낸다."""

    def __init__(self) -> None:
        self.uploaded: dict[str, bytes] = {}

    def upload(self, path: str, content: bytes, content_type: str) -> None:
        self.uploaded[path] = content

    def delete(self, path: str) -> None:
        self.uploaded.pop(path, None)

    def download(self, path: str) -> bytes:
        return self.uploaded[path]

    def get_used_bytes(self) -> int:
        return sum(len(content) for content in self.uploaded.values())


@pytest.fixture
def fake_object_storage() -> FakeObjectStoragePort:
    return FakeObjectStoragePort()


@pytest.fixture
def attachment_service(
    task_group_repository: FakeTaskGroupRepository,
    fake_object_storage: FakeObjectStoragePort,
) -> AttachmentService:
    return AttachmentService(
        attachment_repository=FakeTaskGroupAttachmentRepository(),
        task_group_repository=task_group_repository,
        object_storage=fake_object_storage,
    )


class FakeTaskRepository(TaskRepository):
    """테스트용 인메모리 TaskRepository.

    도메인 Task가 created_at을 갖게 되면서(화면에서 '등록 08-05'를 보여줘야
    해서 추가했다), view='default'의 '최근 30일 이내 등록된 보류' 규칙을
    실제 SQL 리포지토리와 동일하게 재현한다. 예전에는 이 값이 없어서
    상태만 흉내 냈고 시간 기준은 Swagger로 확인할 수밖에 없었다.
    """

    def __init__(self) -> None:
        self._store: dict[int, Task] = {}
        self._next_id = 1

    def add(self, task: Task) -> Task:
        task.id = self._next_id
        if task.created_at is None:
            task.created_at = datetime.now(timezone.utc)
        self._store[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task | None:
        return self._store.get(task_id)

    def list(self, task_group_id: int, view: str = "default") -> list[Task]:
        values = [t for t in self._store.values() if t.task_group_id == task_group_id]
        if view == "default":
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            values = [
                t
                for t in values
                if t.status == TaskStatus.IN_PROGRESS
                or (t.status == TaskStatus.PENDING and t.created_at >= cutoff)
            ]
        return values

    def update(self, task: Task) -> Task:
        self._store[task.id] = task
        return task

    def delete(self, task_id: int) -> None:
        self._store.pop(task_id, None)

    def count_by_status_bulk(
        self, task_group_ids: list[int]
    ) -> dict[int, dict[TaskStatus, int]]:
        result: dict[int, dict[TaskStatus, int]] = {}
        for task in self._store.values():
            if task.task_group_id in task_group_ids:
                counts = result.setdefault(task.task_group_id, {})
                counts[task.status] = counts.get(task.status, 0) + 1
        return result


class FakeTaskActivityLogRepository(TaskActivityLogRepository):
    def __init__(self) -> None:
        self._store: list[TaskActivityLog] = []
        self._next_id = 1

    def add(self, log: TaskActivityLog) -> TaskActivityLog:
        log.id = self._next_id
        self._next_id += 1
        self._store.append(log)
        return log

    def list(self, task_id: int) -> list[TaskActivityLog]:
        return [log for log in self._store if log.task_id == task_id]

    def delete_by_task(self, task_id: int) -> None:
        self._store = [log for log in self._store if log.task_id != task_id]


class FakeTaskCommentRepository(TaskCommentRepository):
    def __init__(self) -> None:
        self._store: dict[int, TaskComment] = {}
        self._next_id = 1

    def add(self, comment: TaskComment) -> TaskComment:
        comment.id = self._next_id
        self._store[comment.id] = comment
        self._next_id += 1
        return comment

    def get(self, comment_id: int) -> TaskComment | None:
        return self._store.get(comment_id)

    def list(self, task_id: int) -> list[TaskComment]:
        return [c for c in self._store.values() if c.task_id == task_id]

    def update(self, comment: TaskComment) -> TaskComment:
        self._store[comment.id] = comment
        return comment

    def delete(self, comment_id: int) -> None:
        self._store.pop(comment_id, None)

    def delete_by_task(self, task_id: int) -> None:
        self._store = {cid: c for cid, c in self._store.items() if c.task_id != task_id}


@pytest.fixture
def task_repository() -> FakeTaskRepository:
    return FakeTaskRepository()


@pytest.fixture
def activity_log_repository() -> FakeTaskActivityLogRepository:
    return FakeTaskActivityLogRepository()


@pytest.fixture
def task_comment_repository() -> FakeTaskCommentRepository:
    return FakeTaskCommentRepository()


@pytest.fixture
def holiday_calendar_port() -> FakeHolidayCalendarPort:
    return FakeHolidayCalendarPort()


@pytest.fixture
def task_service(
    task_repository: FakeTaskRepository,
    activity_log_repository: FakeTaskActivityLogRepository,
    task_comment_repository: FakeTaskCommentRepository,
    assignee_repository: FakeTaskAssigneeRepository,
    dependency_repository: FakeTaskDependencyRepository,
    meeting_task_repository: FakeMeetingTaskRepository,
    task_group_repository: FakeTaskGroupRepository,
    holiday_calendar_port: FakeHolidayCalendarPort,
) -> TaskService:
    return TaskService(
        task_repository=task_repository,
        activity_log_repository=activity_log_repository,
        comment_repository=task_comment_repository,
        assignee_repository=assignee_repository,
        dependency_repository=dependency_repository,
        meeting_task_repository=meeting_task_repository,
        task_group_repository=task_group_repository,
        holiday_calendar=holiday_calendar_port,
    )


@pytest.fixture
def task_comment_service(
    task_comment_repository: FakeTaskCommentRepository,
    task_repository: FakeTaskRepository,
) -> TaskCommentService:
    return TaskCommentService(
        comment_repository=task_comment_repository, task_repository=task_repository
    )


class FakeTaskAssigneeRepository(TaskAssigneeRepository):
    def __init__(self) -> None:
        self._store: set[tuple[int, int]] = set()

    def add(self, task_id: int, person_id: int) -> None:
        self._store.add((task_id, person_id))

    def remove(self, task_id: int, person_id: int) -> None:
        self._store.discard((task_id, person_id))

    def exists(self, task_id: int, person_id: int) -> bool:
        return (task_id, person_id) in self._store

    def list_person_ids(self, task_id: int) -> list[int]:
        return [pid for (tid, pid) in self._store if tid == task_id]

    def delete_by_task(self, task_id: int) -> None:
        self._store = {pair for pair in self._store if pair[0] != task_id}

    def is_person_referenced(self, person_id: int) -> bool:
        return any(pid == person_id for (_, pid) in self._store)


class FakeTaskDependencyRepository(TaskDependencyRepository):
    def __init__(self) -> None:
        self._store: set[tuple[int, int]] = set()

    def add(self, task_id: int, depends_on_task_id: int) -> None:
        self._store.add((task_id, depends_on_task_id))

    def remove(self, task_id: int, depends_on_task_id: int) -> None:
        self._store.discard((task_id, depends_on_task_id))

    def exists(self, task_id: int, depends_on_task_id: int) -> bool:
        return (task_id, depends_on_task_id) in self._store

    def list_depends_on_ids(self, task_id: int) -> list[int]:
        return [d for (t, d) in self._store if t == task_id]

    def delete_by_task(self, task_id: int) -> None:
        self._store = {pair for pair in self._store if task_id not in pair}


@pytest.fixture
def assignee_repository() -> FakeTaskAssigneeRepository:
    return FakeTaskAssigneeRepository()


@pytest.fixture
def dependency_repository() -> FakeTaskDependencyRepository:
    return FakeTaskDependencyRepository()


@pytest.fixture
def task_assignee_service(
    assignee_repository: FakeTaskAssigneeRepository,
    task_repository: FakeTaskRepository,
    person_repository: FakePersonRepository,
    activity_log_repository: FakeTaskActivityLogRepository,
) -> TaskAssigneeService:
    return TaskAssigneeService(
        assignee_repository=assignee_repository,
        task_repository=task_repository,
        person_repository=person_repository,
        activity_log_repository=activity_log_repository,
    )


@pytest.fixture
def task_dependency_service(
    dependency_repository: FakeTaskDependencyRepository,
    task_repository: FakeTaskRepository,
) -> TaskDependencyService:
    return TaskDependencyService(
        dependency_repository=dependency_repository, task_repository=task_repository
    )


class FakeMeetingRepository(MeetingRepository):
    def __init__(self) -> None:
        self._store: dict[int, Meeting] = {}
        self._next_id = 1

    def add(self, meeting: Meeting) -> Meeting:
        meeting.id = self._next_id
        self._store[meeting.id] = meeting
        self._next_id += 1
        return meeting

    def get(self, meeting_id: int) -> Meeting | None:
        return self._store.get(meeting_id)

    def list(self, task_group_id: int) -> list[Meeting]:
        return [m for m in self._store.values() if m.task_group_id == task_group_id]

    def update(self, meeting: Meeting) -> Meeting:
        self._store[meeting.id] = meeting
        return meeting

    def delete(self, meeting_id: int) -> None:
        self._store.pop(meeting_id, None)


class FakeMeetingAttendeeRepository(MeetingAttendeeRepository):
    def __init__(self) -> None:
        self._store: set[tuple[int, int]] = set()

    def add(self, meeting_id: int, person_id: int) -> None:
        self._store.add((meeting_id, person_id))

    def remove(self, meeting_id: int, person_id: int) -> None:
        self._store.discard((meeting_id, person_id))

    def exists(self, meeting_id: int, person_id: int) -> bool:
        return (meeting_id, person_id) in self._store

    def list_person_ids(self, meeting_id: int) -> list[int]:
        return [pid for (mid, pid) in self._store if mid == meeting_id]

    def delete_by_meeting(self, meeting_id: int) -> None:
        self._store = {pair for pair in self._store if pair[0] != meeting_id}

    def is_person_referenced(self, person_id: int) -> bool:
        return any(pid == person_id for (_, pid) in self._store)


class FakeMeetingTaskRepository(MeetingTaskRepository):
    def __init__(self) -> None:
        self._store: set[tuple[int, int]] = set()

    def add(self, meeting_id: int, task_id: int) -> None:
        self._store.add((meeting_id, task_id))

    def remove(self, meeting_id: int, task_id: int) -> None:
        self._store.discard((meeting_id, task_id))

    def exists(self, meeting_id: int, task_id: int) -> bool:
        return (meeting_id, task_id) in self._store

    def list_task_ids(self, meeting_id: int) -> list[int]:
        return [tid for (mid, tid) in self._store if mid == meeting_id]

    def list_meeting_ids_by_task(self, task_id: int) -> list[int]:
        return [mid for (mid, tid) in self._store if tid == task_id]

    def delete_by_meeting(self, meeting_id: int) -> None:
        self._store = {pair for pair in self._store if pair[0] != meeting_id}

    def delete_by_task(self, task_id: int) -> None:
        self._store = {pair for pair in self._store if pair[1] != task_id}


@pytest.fixture
def meeting_repository() -> FakeMeetingRepository:
    return FakeMeetingRepository()


@pytest.fixture
def meeting_attendee_repository() -> FakeMeetingAttendeeRepository:
    return FakeMeetingAttendeeRepository()


@pytest.fixture
def meeting_task_repository() -> FakeMeetingTaskRepository:
    return FakeMeetingTaskRepository()


@pytest.fixture
def meeting_service(
    meeting_repository: FakeMeetingRepository,
    meeting_attendee_repository: FakeMeetingAttendeeRepository,
    meeting_task_repository: FakeMeetingTaskRepository,
    task_group_repository: FakeTaskGroupRepository,
) -> MeetingService:
    return MeetingService(
        meeting_repository=meeting_repository,
        attendee_repository=meeting_attendee_repository,
        task_link_repository=meeting_task_repository,
        task_group_repository=task_group_repository,
    )


@pytest.fixture
def meeting_attendee_service(
    meeting_attendee_repository: FakeMeetingAttendeeRepository,
    meeting_repository: FakeMeetingRepository,
    person_repository: FakePersonRepository,
) -> MeetingAttendeeService:
    return MeetingAttendeeService(
        attendee_repository=meeting_attendee_repository,
        meeting_repository=meeting_repository,
        person_repository=person_repository,
    )


@pytest.fixture
def meeting_task_service(
    meeting_task_repository: FakeMeetingTaskRepository,
    meeting_repository: FakeMeetingRepository,
    task_repository: FakeTaskRepository,
) -> MeetingTaskService:
    return MeetingTaskService(
        task_link_repository=meeting_task_repository,
        meeting_repository=meeting_repository,
        task_repository=task_repository,
    )


class FakeHolidayCalendarPort(HolidayCalendarPort):
    """테스트용 공휴일 제공자. 실제 달력과 무관하게 원하는 날만 공휴일로
    지정해서 마감일 계산 로직만 격리해 검증한다."""

    def __init__(self, holidays: set[date] | None = None) -> None:
        self.holidays: set[date] = holidays or set()

    def is_holiday(self, day: date) -> bool:
        return day in self.holidays


class FakeDatabaseUsagePort(DatabaseUsagePort):
    def __init__(self, used_bytes: int = 0) -> None:
        self.used_bytes = used_bytes

    def get_used_bytes(self) -> int:
        return self.used_bytes


class FakeStorageUsageSnapshotRepository(StorageUsageSnapshotRepository):
    def __init__(self) -> None:
        self._snapshot_dates: set[date] = set()
        self.add_call_count = 0

    def has_snapshot_for_today(self) -> bool:
        return date.today() in self._snapshot_dates

    def add(self, db_used_bytes: int, object_storage_used_bytes: int) -> None:
        self._snapshot_dates.add(date.today())
        self.add_call_count += 1


class FakeTaskGroupSizeEstimator(TaskGroupSizeEstimator):
    def __init__(self, fixed_bytes: int = 0) -> None:
        self.fixed_bytes = fixed_bytes

    def estimate_content_bytes(self, task_group_id: int) -> int:
        return self.fixed_bytes


class FakeExportJobRepository(ExportJobRepository):
    def __init__(self) -> None:
        self._jobs: dict[int, ExportJob] = {}
        self._links: dict[tuple[int, int], ExportJobTaskGroup] = {}
        self._next_id = 1

    def add(self, task_group_ids: list[int]) -> ExportJob:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        job = ExportJob(id=self._next_id, requested_at=now, completed_at=now)
        self._jobs[job.id] = job
        for task_group_id in task_group_ids:
            self._links[(job.id, task_group_id)] = ExportJobTaskGroup(
                export_job_id=job.id, task_group_id=task_group_id
            )
        self._next_id += 1
        return job

    def get(self, export_job_id: int) -> ExportJob | None:
        return self._jobs.get(export_job_id)

    def list(self) -> list[ExportJob]:
        return list(self._jobs.values())

    def get_link(
        self, export_job_id: int, task_group_id: int
    ) -> ExportJobTaskGroup | None:
        return self._links.get((export_job_id, task_group_id))

    def list_links(self, export_job_id: int) -> list[ExportJobTaskGroup]:
        return [link for (jid, _), link in self._links.items() if jid == export_job_id]

    def update_link(self, link: ExportJobTaskGroup) -> ExportJobTaskGroup:
        self._links[(link.export_job_id, link.task_group_id)] = link
        return link


@pytest.fixture
def database_usage_port() -> FakeDatabaseUsagePort:
    return FakeDatabaseUsagePort(used_bytes=1_000_000)


@pytest.fixture
def storage_usage_snapshot_repository() -> FakeStorageUsageSnapshotRepository:
    return FakeStorageUsageSnapshotRepository()


@pytest.fixture
def storage_service(
    database_usage_port: FakeDatabaseUsagePort,
    fake_object_storage: FakeObjectStoragePort,
    storage_usage_snapshot_repository: FakeStorageUsageSnapshotRepository,
) -> StorageService:
    return StorageService(
        database_usage=database_usage_port,
        object_storage=fake_object_storage,
        snapshot_repository=storage_usage_snapshot_repository,
    )


@pytest.fixture
def export_job_repository() -> FakeExportJobRepository:
    return FakeExportJobRepository()


@pytest.fixture
def task_group_size_estimator() -> FakeTaskGroupSizeEstimator:
    return FakeTaskGroupSizeEstimator(fixed_bytes=500)


@pytest.fixture
def export_service(
    export_job_repository: FakeExportJobRepository,
    task_group_repository: FakeTaskGroupRepository,
    task_group_service: TaskGroupService,
    task_service: TaskService,
    task_comment_service: TaskCommentService,
    meeting_service: MeetingService,
    attachment_service: AttachmentService,
    fake_object_storage: FakeObjectStoragePort,
) -> ExportService:
    return ExportService(
        export_job_repository=export_job_repository,
        task_group_repository=task_group_repository,
        task_group_service=task_group_service,
        task_service=task_service,
        task_comment_service=task_comment_service,
        meeting_service=meeting_service,
        attachment_service=attachment_service,
        object_storage=fake_object_storage,
    )


class FakeHolidayCalendarPort(HolidayCalendarPort):
    """테스트용 공휴일 제공자. 실제 달력과 무관하게 원하는 날만 공휴일로
    지정해서 마감일 계산 로직만 격리해 검증한다."""

    def __init__(self, holidays: set[date] | None = None) -> None:
        self.holidays: set[date] = holidays or set()

    def is_holiday(self, day: date) -> bool:
        return day in self.holidays


@pytest.fixture
def holiday_calendar_port() -> FakeHolidayCalendarPort:
    return FakeHolidayCalendarPort()

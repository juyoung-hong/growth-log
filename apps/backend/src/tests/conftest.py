"""공용 pytest fixture. tests/ 하위 모든 테스트에서 바로 쓸 수 있다."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from application.ports.outbound.object_storage_port import ObjectStoragePort
from application.ports.outbound.person_repository import PersonRepository
from application.ports.outbound.task_activity_log_repository import (
    TaskActivityLogRepository,
)
from application.ports.outbound.task_comment_repository import TaskCommentRepository
from application.ports.outbound.task_group_attachment_repository import (
    TaskGroupAttachmentRepository,
)
from application.ports.outbound.task_group_repository import TaskGroupRepository
from application.ports.outbound.task_repository import TaskRepository
from application.services.attachment_service import AttachmentService
from application.services.person_service import PersonService
from application.services.task_comment_service import TaskCommentService
from application.services.task_group_service import TaskGroupService
from application.services.task_service import TaskService
from domain.common.enums import Scope, TaskStatus
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
        return False


@pytest.fixture
def person_service() -> PersonService:
    """DB 없이 동작하는 PersonService. 매 테스트마다 빈 저장소로 새로 시작한다."""
    return PersonService(FakePersonRepository())


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

    view='default' 필터는 상태만 흉내 낸다(진행중 + 보류를 포함) — 실제
    SQL 리포지토리처럼 '최근 30일 이내 등록된 보류'까지 정확히 재현하려면
    도메인 Task에 created_at을 노출해야 하는데, Person/TaskGroup도 도메인에
    created_at을 안 두는 원칙이라 여기서도 안 둔다. 그 시간 기준 세부
    동작은 Swagger로 직접 확인한다(17절).
    """

    def __init__(self) -> None:
        self._store: dict[int, Task] = {}
        self._next_id = 1

    def add(self, task: Task) -> Task:
        task.id = self._next_id
        self._store[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task | None:
        return self._store.get(task_id)

    def list(self, task_group_id: int, view: str = "default") -> list[Task]:
        values = [t for t in self._store.values() if t.task_group_id == task_group_id]
        if view == "default":
            values = [t for t in values if t.status != TaskStatus.DONE]
        return values

    def update(self, task: Task) -> Task:
        self._store[task.id] = task
        return task

    def delete(self, task_id: int) -> None:
        self._store.pop(task_id, None)


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
def task_service(
    task_repository: FakeTaskRepository,
    activity_log_repository: FakeTaskActivityLogRepository,
    task_comment_repository: FakeTaskCommentRepository,
    task_group_repository: FakeTaskGroupRepository,
) -> TaskService:
    return TaskService(
        task_repository=task_repository,
        activity_log_repository=activity_log_repository,
        comment_repository=task_comment_repository,
        task_group_repository=task_group_repository,
    )


@pytest.fixture
def task_comment_service(
    task_comment_repository: FakeTaskCommentRepository,
    task_repository: FakeTaskRepository,
) -> TaskCommentService:
    return TaskCommentService(
        comment_repository=task_comment_repository, task_repository=task_repository
    )

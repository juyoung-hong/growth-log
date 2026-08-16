from typing import Iterator

from fastapi import Depends
from sqlmodel import Session

from adapters.outbound.oci_object_storage.oci_object_storage_adapter import (
    object_storage_adapter,
)
from adapters.outbound.oracle_adb_26ai.person_repository import SqlPersonRepository
from adapters.outbound.oracle_adb_26ai.session import engine
from adapters.outbound.oracle_adb_26ai.task_activity_log_repository import (
    SqlTaskActivityLogRepository,
)
from adapters.outbound.oracle_adb_26ai.task_comment_repository import (
    SqlTaskCommentRepository,
)
from adapters.outbound.oracle_adb_26ai.task_group_attachment_repository import (
    SqlTaskGroupAttachmentRepository,
)
from adapters.outbound.oracle_adb_26ai.task_group_repository import (
    SqlTaskGroupRepository,
)
from adapters.outbound.oracle_adb_26ai.task_repository import SqlTaskRepository
from application.services.attachment_service import AttachmentService
from application.services.person_service import PersonService
from application.services.task_comment_service import TaskCommentService
from application.services.task_group_service import TaskGroupService
from application.services.task_service import TaskService


def get_db_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


def get_person_service(session: Session = Depends(get_db_session)) -> PersonService:
    return PersonService(SqlPersonRepository(session))


def get_task_group_service(
    session: Session = Depends(get_db_session),
) -> TaskGroupService:
    return TaskGroupService(SqlTaskGroupRepository(session))


def get_attachment_service(
    session: Session = Depends(get_db_session),
) -> AttachmentService:
    return AttachmentService(
        attachment_repository=SqlTaskGroupAttachmentRepository(session),
        task_group_repository=SqlTaskGroupRepository(session),
        object_storage=object_storage_adapter,
    )


def get_task_service(session: Session = Depends(get_db_session)) -> TaskService:
    return TaskService(
        task_repository=SqlTaskRepository(session),
        activity_log_repository=SqlTaskActivityLogRepository(session),
        comment_repository=SqlTaskCommentRepository(session),
        task_group_repository=SqlTaskGroupRepository(session),
    )


def get_task_comment_service(
    session: Session = Depends(get_db_session),
) -> TaskCommentService:
    return TaskCommentService(
        comment_repository=SqlTaskCommentRepository(session),
        task_repository=SqlTaskRepository(session),
    )

from typing import Iterator

from fastapi import Depends
from sqlmodel import Session

from adapters.outbound.oci_object_storage.oci_object_storage_adapter import (
    object_storage_adapter,
)
from adapters.outbound.oracle_adb_26ai.person_repository import SqlPersonRepository
from adapters.outbound.oracle_adb_26ai.session import engine
from adapters.outbound.oracle_adb_26ai.task_group_attachment_repository import (
    SqlTaskGroupAttachmentRepository,
)
from adapters.outbound.oracle_adb_26ai.task_group_repository import (
    SqlTaskGroupRepository,
)
from application.services.attachment_service import AttachmentService
from application.services.person_service import PersonService
from application.services.task_group_service import TaskGroupService


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

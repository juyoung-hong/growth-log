from typing import Iterator

from fastapi import Depends
from sqlmodel import Session

from adapters.outbound.holiday.kr_holiday_adapter import holiday_calendar_adapter
from adapters.outbound.oci_database.oci_database_usage_adapter import (
    database_usage_adapter,
)
from adapters.outbound.oci_object_storage.oci_object_storage_adapter import (
    object_storage_adapter,
)
from adapters.outbound.oracle_adb_26ai.export_job_repository import (
    SqlExportJobRepository,
)
from adapters.outbound.oracle_adb_26ai.meeting_attendee_repository import (
    SqlMeetingAttendeeRepository,
)
from adapters.outbound.oracle_adb_26ai.meeting_repository import SqlMeetingRepository
from adapters.outbound.oracle_adb_26ai.meeting_task_repository import (
    SqlMeetingTaskRepository,
)
from adapters.outbound.oracle_adb_26ai.person_repository import SqlPersonRepository
from adapters.outbound.oracle_adb_26ai.session import engine
from adapters.outbound.oracle_adb_26ai.storage_usage_snapshot_repository import (
    SqlStorageUsageSnapshotRepository,
)
from adapters.outbound.oracle_adb_26ai.task_activity_log_repository import (
    SqlTaskActivityLogRepository,
)
from adapters.outbound.oracle_adb_26ai.task_assignee_repository import (
    SqlTaskAssigneeRepository,
)
from adapters.outbound.oracle_adb_26ai.task_comment_repository import (
    SqlTaskCommentRepository,
)
from adapters.outbound.oracle_adb_26ai.task_dependency_repository import (
    SqlTaskDependencyRepository,
)
from adapters.outbound.oracle_adb_26ai.task_group_attachment_repository import (
    SqlTaskGroupAttachmentRepository,
)
from adapters.outbound.oracle_adb_26ai.task_group_repository import (
    SqlTaskGroupRepository,
)
from adapters.outbound.oracle_adb_26ai.task_group_size_estimator import (
    SqlTaskGroupSizeEstimator,
)
from adapters.outbound.oracle_adb_26ai.task_repository import SqlTaskRepository
from application.ports.outbound.task_group_size_estimator import TaskGroupSizeEstimator
from application.services.attachment_service import AttachmentService
from application.services.export_service import ExportService
from application.services.holiday_service import HolidayService
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


def get_db_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


def get_person_service(session: Session = Depends(get_db_session)) -> PersonService:
    return PersonService(SqlPersonRepository(session))


def get_task_group_service(
    session: Session = Depends(get_db_session),
) -> TaskGroupService:
    return TaskGroupService(SqlTaskGroupRepository(session))


def get_holiday_service() -> HolidayService:
    return HolidayService(holiday_calendar=holiday_calendar_adapter)


def get_attachment_service(
    session: Session = Depends(get_db_session),
) -> AttachmentService:
    return AttachmentService(
        attachment_repository=SqlTaskGroupAttachmentRepository(session),
        task_group_repository=SqlTaskGroupRepository(session),
        object_storage=object_storage_adapter,
    )


def get_task_assignee_service(
    session: Session = Depends(get_db_session),
) -> TaskAssigneeService:
    return TaskAssigneeService(
        assignee_repository=SqlTaskAssigneeRepository(session),
        task_repository=SqlTaskRepository(session),
        person_repository=SqlPersonRepository(session),
        activity_log_repository=SqlTaskActivityLogRepository(session),
    )


def get_task_dependency_service(
    session: Session = Depends(get_db_session),
) -> TaskDependencyService:
    return TaskDependencyService(
        dependency_repository=SqlTaskDependencyRepository(session),
        task_repository=SqlTaskRepository(session),
        activity_log_repository=SqlTaskActivityLogRepository(session),
    )


def get_task_comment_service(
    session: Session = Depends(get_db_session),
) -> TaskCommentService:
    return TaskCommentService(
        comment_repository=SqlTaskCommentRepository(session),
        task_repository=SqlTaskRepository(session),
    )


def get_task_service(session: Session = Depends(get_db_session)) -> TaskService:
    return TaskService(
        task_repository=SqlTaskRepository(session),
        activity_log_repository=SqlTaskActivityLogRepository(session),
        comment_repository=SqlTaskCommentRepository(session),
        assignee_repository=SqlTaskAssigneeRepository(session),
        dependency_repository=SqlTaskDependencyRepository(session),
        meeting_task_repository=SqlMeetingTaskRepository(session),
        task_group_repository=SqlTaskGroupRepository(session),
        holiday_calendar=holiday_calendar_adapter,
    )


def get_meeting_service(session: Session = Depends(get_db_session)) -> MeetingService:
    return MeetingService(
        meeting_repository=SqlMeetingRepository(session),
        attendee_repository=SqlMeetingAttendeeRepository(session),
        task_link_repository=SqlMeetingTaskRepository(session),
        task_group_repository=SqlTaskGroupRepository(session),
    )


def get_meeting_attendee_service(
    session: Session = Depends(get_db_session),
) -> MeetingAttendeeService:
    return MeetingAttendeeService(
        attendee_repository=SqlMeetingAttendeeRepository(session),
        meeting_repository=SqlMeetingRepository(session),
        person_repository=SqlPersonRepository(session),
    )


def get_meeting_task_service(
    session: Session = Depends(get_db_session),
) -> MeetingTaskService:
    return MeetingTaskService(
        task_link_repository=SqlMeetingTaskRepository(session),
        meeting_repository=SqlMeetingRepository(session),
        task_repository=SqlTaskRepository(session),
    )


def get_storage_service(session: Session = Depends(get_db_session)) -> StorageService:
    return StorageService(
        database_usage=database_usage_adapter,
        object_storage=object_storage_adapter,
        snapshot_repository=SqlStorageUsageSnapshotRepository(session),
    )


def get_export_service(session: Session = Depends(get_db_session)) -> ExportService:
    return ExportService(
        export_job_repository=SqlExportJobRepository(session),
        task_group_repository=SqlTaskGroupRepository(session),
        task_group_service=TaskGroupService(SqlTaskGroupRepository(session)),
        task_service=TaskService(
            task_repository=SqlTaskRepository(session),
            activity_log_repository=SqlTaskActivityLogRepository(session),
            comment_repository=SqlTaskCommentRepository(session),
            assignee_repository=SqlTaskAssigneeRepository(session),
            dependency_repository=SqlTaskDependencyRepository(session),
            meeting_task_repository=SqlMeetingTaskRepository(session),
            task_group_repository=SqlTaskGroupRepository(session),
        ),
        task_comment_service=TaskCommentService(
            comment_repository=SqlTaskCommentRepository(session),
            task_repository=SqlTaskRepository(session),
        ),
        meeting_service=MeetingService(
            meeting_repository=SqlMeetingRepository(session),
            attendee_repository=SqlMeetingAttendeeRepository(session),
            task_link_repository=SqlMeetingTaskRepository(session),
            task_group_repository=SqlTaskGroupRepository(session),
        ),
        attachment_service=AttachmentService(
            attachment_repository=SqlTaskGroupAttachmentRepository(session),
            task_group_repository=SqlTaskGroupRepository(session),
            object_storage=object_storage_adapter,
        ),
        object_storage=object_storage_adapter,
    )


def get_task_group_size_estimator(
    session: Session = Depends(get_db_session),
) -> TaskGroupSizeEstimator:
    return SqlTaskGroupSizeEstimator(session)

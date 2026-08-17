"""ExportService 유스케이스를 Fake로 DB/OCI 없이 검증한다."""

from __future__ import annotations

import io
import zipfile

import pytest

from application.services.export_service import ExportService
from domain.common.enums import Scope
from domain.exceptions import ExportLinkNotFoundError, TaskGroupNotFoundError
from domain.task_group import TaskGroup


def test_export를_생성한다(
    export_service: ExportService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    job = export_service.create_export([task_group.id])

    assert job.id is not None
    links = export_service.list_links(job.id)
    assert [link.task_group_id for link in links] == [task_group.id]


def test_없는_TaskGroup으로_export_생성하면_예외(export_service: ExportService) -> None:
    with pytest.raises(TaskGroupNotFoundError):
        export_service.create_export([999])


def test_zip에_csv와_첨부파일이_들어간다(
    export_service: ExportService,
    task_group_repository,
    task_service,
    attachment_service,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task_service.create(task_group_id=task_group.id, name="작업")
    attachment_service.create_file_attachment(
        task_group_id=task_group.id,
        title="자료.txt",
        content=b"hello",
        mime_type="text/plain",
    )
    job = export_service.create_export([task_group.id])

    content = export_service.build_zip(job.id)

    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        names = zf.namelist()
        assert "task_groups.csv" in names
        assert "tasks.csv" in names
        assert any(
            n.startswith("attachments/") and n.endswith("자료.txt") for n in names
        )


def test_아카이브_삭제_상태를_기록한다(
    export_service: ExportService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    job = export_service.create_export([task_group.id])

    export_service.mark_deleted(
        job.id, task_group.id, db_bytes_freed=100, object_storage_bytes_freed=200
    )

    link = export_service.get_link(job.id, task_group.id)
    assert link.is_source_deleted is True
    assert link.db_bytes_freed == 100


def test_없는_링크를_조회하면_예외(export_service: ExportService) -> None:
    with pytest.raises(ExportLinkNotFoundError):
        export_service.get_link(999, 999)

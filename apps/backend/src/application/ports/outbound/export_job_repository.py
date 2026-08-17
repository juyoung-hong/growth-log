"""Export 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.export_job import ExportJob, ExportJobTaskGroup


class ExportJobRepository(ABC):
    @abstractmethod
    def add(self, task_group_ids: list[int]) -> ExportJob:
        """ExportJob과 각 TaskGroup에 대한 연결(ExportJobTaskGroup)을 함께 만든다."""
        raise NotImplementedError

    @abstractmethod
    def get(self, export_job_id: int) -> ExportJob | None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[ExportJob]:
        raise NotImplementedError

    @abstractmethod
    def get_link(
        self, export_job_id: int, task_group_id: int
    ) -> ExportJobTaskGroup | None:
        raise NotImplementedError

    @abstractmethod
    def list_links(self, export_job_id: int) -> list[ExportJobTaskGroup]:
        raise NotImplementedError

    @abstractmethod
    def update_link(self, link: ExportJobTaskGroup) -> ExportJobTaskGroup:
        raise NotImplementedError

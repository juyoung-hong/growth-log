"""저장공간 사용량 스냅샷 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod


class StorageUsageSnapshotRepository(ABC):
    @abstractmethod
    def has_snapshot_for_today(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def add(self, db_used_bytes: int, object_storage_used_bytes: int) -> None:
        raise NotImplementedError

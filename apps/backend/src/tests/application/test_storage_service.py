"""StorageService 유스케이스를 Fake로 DB/OCI 없이 검증한다."""

from __future__ import annotations

from application.services.storage_service import StorageService


def test_사용량을_조회한다(storage_service: StorageService) -> None:
    usage = storage_service.get_usage()
    assert usage.db_used_bytes == 1_000_000


def test_같은_날_두번_조회해도_스냅샷은_한번만_쌓인다(
    storage_service: StorageService, storage_usage_snapshot_repository
) -> None:
    storage_service.get_usage()
    storage_service.get_usage()
    assert storage_usage_snapshot_repository.add_call_count == 1

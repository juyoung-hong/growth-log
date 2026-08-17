"""저장공간 사용량 도메인 모델."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StorageUsage:
    """현재 시점의 DB·Object Storage 사용량(바이트). 한도·퍼센트·경고는
    API 상수를 아는 스키마/라우터 계층의 책임이라 여기 안 둔다."""

    db_used_bytes: int
    object_storage_used_bytes: int

"""Oracle ADB 실제 사용 용량 조회 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod


class DatabaseUsagePort(ABC):
    @abstractmethod
    def get_used_bytes(self) -> int:
        """Autonomous Database가 현재 실제로 사용 중인 스토리지 크기(바이트)."""
        raise NotImplementedError

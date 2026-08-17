"""TaskGroup 하위 콘텐츠 크기 추정 포트. 아카이브 삭제 시 db_bytes_freed 계산에 쓰인다."""

from __future__ import annotations

from abc import ABC, abstractmethod


class TaskGroupSizeEstimator(ABC):
    @abstractmethod
    def estimate_content_bytes(self, task_group_id: int) -> int:
        """이 TaskGroup 하위 텍스트 콘텐츠의 실제 바이트 합. 추측이 아니라
        삭제 직전 실제 값을 측정한 근사치다(0번 섹션 ② 참고)."""
        raise NotImplementedError

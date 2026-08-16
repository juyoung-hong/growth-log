"""Task 댓글(TaskComment) 도메인 모델."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.common.validators import validate_not_empty


@dataclass
class TaskComment:
    """Task에 달린 댓글. 수정 시 이력을 남기지 않고 그대로 덮어쓴다."""

    id: int | None
    task_id: int
    content: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        validate_not_empty(self.content, field="content")

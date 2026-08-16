"""TaskGroup(작업 그룹) 도메인 모델.

프로젝트·목표처럼 여러 Task를 묶는 상위 개체. Person과 마찬가지로
프레임워크 의존성이 없는 순수 파이썬이다.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.common.enums import Scope, TaskStatus
from domain.common.validators import validate_not_empty


@dataclass
class TaskGroup:
    """작업 그룹. 여러 Task를 묶는 상위 단위."""

    id: int | None
    category: Scope
    name: str
    description: str | None = None
    status: TaskStatus = TaskStatus.IN_PROGRESS
    is_archived: bool = False

    def __post_init__(self) -> None:
        validate_not_empty(self.name, field="name")

"""Task 활동이력(TaskActivityLog) 도메인 모델.

Task의 등록·상태·담당자·일정·완료 이벤트를 시간순으로 남긴다. 사람이 직접
만들지 않고, TaskService의 각 액션이 부수효과로 기록한다(수동 등록
엔드포인트가 없다).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ActivityEventType(str, Enum):
    """활동이력 이벤트 종류. '담당자'는 5단계(담당자 기능)부터 실제로 쓰인다."""

    REGISTERED = "등록"
    STATUS = "상태"
    ASSIGNEE = "담당자"
    SCHEDULE = "일정"
    COMPLETED = "완료"


@dataclass
class TaskActivityLog:
    """Task에 대한 활동이력 한 건."""

    id: int | None
    task_id: int
    event_type: ActivityEventType
    old_value: str | None = None
    new_value: str | None = None
    reason: str | None = None
    event_at: datetime | None = None

"""Meeting(미팅) 도메인 모델.

TaskGroup에 속한 미팅. 사전에 일정만 잡아두고(예정), 끝나면 내용을
채우는(완료) 생애주기를 가진다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MeetingStatus(str, Enum):
    """미팅 상태. Task/TaskGroup의 TaskStatus와 값이 달라 공유하지 않는다."""

    SCHEDULED = "예정"
    DONE = "완료"


@dataclass
class Meeting:
    """TaskGroup에 속한 미팅."""

    id: int | None
    task_group_id: int
    scheduled_at: datetime
    status: MeetingStatus = MeetingStatus.SCHEDULED
    agenda: str | None = None
    content: str | None = None

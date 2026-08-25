"""TaskGroup 응답 조립(_build_read)을 확인한다.

이 파일이 있는 이유: 커버리지 측정 대상은 domain과 application.services라
adapters/inbound는 빠져 있다. 그런데 TaskGroupRead에 created_at을 추가했을 때
실제로 깨진 곳은 필드별로 응답을 직접 만드는 이 조립부였다 — 기본값이 없는
필수 필드라 하나만 빠져도 ValidationError가 난다. 서비스 테스트로는 잡히지
않는 자리라 여기서 따로 붙잡는다.
"""

from __future__ import annotations

from datetime import datetime, timezone

from adapters.inbound.api.v1.task_groups import _build_read
from domain.common.enums import Scope, TaskStatus
from domain.task_group import TaskGroup


def _task_group(**overrides) -> TaskGroup:
    defaults = {
        "id": 1,
        "category": Scope.COMPANY,
        "name": "메일서버 이중화 작업",
        "description": "장애 대응력 확보",
        "status": TaskStatus.IN_PROGRESS,
        "created_at": datetime(2026, 8, 5, tzinfo=timezone.utc),
    }
    return TaskGroup(**{**defaults, **overrides})


def test_도메인_필드가_빠짐없이_응답에_실린다() -> None:
    read = _build_read(_task_group(), {})

    assert read.id == 1
    assert read.category == Scope.COMPANY
    assert read.name == "메일서버 이중화 작업"
    assert read.description == "장애 대응력 확보"
    assert read.status == TaskStatus.IN_PROGRESS
    assert read.is_archived is False
    assert read.created_at == datetime(2026, 8, 5, tzinfo=timezone.utc)


def test_진행률을_상태별_개수로_계산한다() -> None:
    counts = {TaskStatus.DONE: 7, TaskStatus.IN_PROGRESS: 2, TaskStatus.PENDING: 1}

    progress = _build_read(_task_group(), counts).progress

    assert progress.total_tasks == 10
    assert progress.done_tasks == 7
    assert progress.percent == 70


def test_Task가_없으면_진행률은_0퍼센트() -> None:
    """0으로 나누지 않고 0%를 돌려줘야 한다."""
    progress = _build_read(_task_group(), {}).progress

    assert progress.total_tasks == 0
    assert progress.done_tasks == 0
    assert progress.percent == 0


def test_진행률은_반올림한다() -> None:
    # 1/3 = 33.33...%
    progress = _build_read(
        _task_group(), {TaskStatus.DONE: 1, TaskStatus.PENDING: 2}
    ).progress

    assert progress.percent == 33

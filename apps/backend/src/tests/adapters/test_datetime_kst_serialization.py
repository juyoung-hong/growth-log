"""API 응답의 datetime 필드가 KST로 나가는지 확인한다.

Oracle TIMESTAMP 컬럼은 시간대 정보 없이 저장되므로 ORM이 읽어오는 값은
항상 naive datetime이다(meeting.py의 scheduled_at에서 처음 정리한 문제,
_datetime.py 참고). TaskRead·TaskActivityLogRead·TaskCommentRead·
TaskGroupRead 넷 다 이 변환을 빠뜨리면 화면에 9시간 늦은 시각이 뜬다 —
@field_serializer 데코레이터가 실제로 붙어 있는지를 여기서 잡는다.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from adapters.inbound.api.schemas._datetime import to_kst_iso
from adapters.inbound.api.schemas.task import TaskActivityLogRead, TaskRead
from adapters.inbound.api.schemas.task_comment import TaskCommentRead
from adapters.inbound.api.schemas.task_group import TaskGroupRead
from domain.common.enums import Scope, TaskStatus


def test_naive_datetime은_UTC로_간주해_KST로_바꾼다() -> None:
    naive = datetime(2026, 8, 16, 0, 0, 0)  # UTC 자정

    assert to_kst_iso(naive) == "2026-08-16T09:00:00+09:00"


def test_이미_시간대가_있으면_그대로_KST로_변환한다() -> None:
    aware_utc = datetime(2026, 8, 16, 0, 0, 0, tzinfo=timezone.utc)

    assert to_kst_iso(aware_utc) == "2026-08-16T09:00:00+09:00"


def _task(**overrides) -> TaskRead:
    defaults = dict(
        id=1,
        task_group_id=1,
        name="이중화 아키텍처 설계",
        status=TaskStatus.IN_PROGRESS,
        estimated_days=4,
        start_date=date(2026, 8, 18),
        due_date=date(2026, 8, 21),
        completed_at=None,
        created_at=datetime(2026, 8, 16, 0, 0, 0),
    )
    return TaskRead(**{**defaults, **overrides})


def test_TaskRead의_created_at이_KST_문자열로_직렬화된다() -> None:
    dumped = _task().model_dump(mode="json")

    assert dumped["created_at"] == "2026-08-16T09:00:00+09:00"


def test_TaskRead의_completed_at이_None이면_None_그대로_직렬화된다() -> None:
    dumped = _task(completed_at=None).model_dump(mode="json")

    assert dumped["completed_at"] is None


def test_TaskActivityLogRead의_event_at이_KST_문자열로_직렬화된다() -> None:
    log = TaskActivityLogRead(
        id=1,
        event_type="상태",
        event_at=datetime(2026, 8, 16, 0, 0, 0),
        old_value="보류",
        new_value="진행중",
        reason=None,
    )

    assert log.model_dump(mode="json")["event_at"] == "2026-08-16T09:00:00+09:00"


def test_TaskCommentRead의_시각_필드가_KST_문자열로_직렬화된다() -> None:
    comment = TaskCommentRead(
        id=1,
        task_id=1,
        content="TTL 300으로 SPF 값 재확인 필요",
        created_at=datetime(2026, 8, 16, 0, 40, 0),
        updated_at=datetime(2026, 8, 16, 0, 40, 0),
    )
    dumped = comment.model_dump(mode="json")

    assert dumped["created_at"] == "2026-08-16T09:40:00+09:00"
    assert dumped["updated_at"] == "2026-08-16T09:40:00+09:00"


def test_TaskGroupRead의_created_at이_KST_문자열로_직렬화된다() -> None:
    task_group = TaskGroupRead(
        id=1,
        category=Scope.COMPANY,
        name="메일서버 이중화",
        description=None,
        status=TaskStatus.IN_PROGRESS,
        is_archived=False,
        created_at=datetime(2026, 8, 1, 0, 0, 0),
    )

    assert (
        task_group.model_dump(mode="json")["created_at"] == "2026-08-01T09:00:00+09:00"
    )

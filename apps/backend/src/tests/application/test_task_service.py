"""TaskService 유스케이스를 Fake로 DB 없이 검증한다."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from application.services.task_service import TaskService
from domain.common.enums import Scope, TaskStatus
from domain.common.exceptions import InvalidFieldError
from domain.exceptions import TaskGroupNotFoundError, TaskNotFoundError
from domain.task_activity_log import ActivityEventType
from domain.task_group import TaskGroup


def test_등록하면_활동이력에_등록_이벤트가_남는다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="설계 문서 작성")

    logs = task_service.list_activity_log(task.id)
    assert len(logs) == 1
    assert logs[0].event_type == ActivityEventType.REGISTERED


def test_없는_TaskGroup에_등록하면_예외(task_service: TaskService) -> None:
    with pytest.raises(TaskGroupNotFoundError):
        task_service.create(task_group_id=999, name="작업")


def test_완료로_바꾸면_completed_at이_채워진다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")

    updated = task_service.change_status(task.id, TaskStatus.DONE)

    assert updated.completed_at is not None
    logs = task_service.list_activity_log(task.id)
    assert logs[-1].event_type == ActivityEventType.COMPLETED


def test_완료에서_다른_상태로_바꾸면_completed_at이_비워진다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    task_service.change_status(task.id, TaskStatus.DONE)

    updated = task_service.change_status(task.id, TaskStatus.IN_PROGRESS)

    assert updated.completed_at is None
    logs = task_service.list_activity_log(task.id)
    assert logs[-1].event_type == ActivityEventType.STATUS


def test_마감일이_시작일보다_빠르면_일정_변경이_거부된다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")

    with pytest.raises(InvalidFieldError):
        task_service.change_schedule(
            task.id, start_date=date(2026, 8, 20), due_date=date(2026, 8, 10)
        )


def test_일정을_변경하면_활동이력에_사유가_남는다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")

    task_service.change_schedule(
        task.id,
        start_date=date(2026, 8, 18),
        due_date=date(2026, 8, 21),
        reason="담당자 휴가로 순연",
    )

    logs = task_service.list_activity_log(task.id)
    assert logs[-1].event_type == ActivityEventType.SCHEDULE
    assert logs[-1].reason == "담당자 휴가로 순연"


def test_삭제하면_활동이력과_댓글도_함께_지워진다(
    task_service: TaskService,
    task_group_repository,
    activity_log_repository,
    task_comment_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    from domain.task_comment import TaskComment

    task_comment_repository.add(TaskComment(id=None, task_id=task.id, content="댓글"))

    task_service.delete(task.id)

    with pytest.raises(TaskNotFoundError):
        task_service.get(task.id)
    assert activity_log_repository.list(task.id) == []
    assert task_comment_repository.list(task.id) == []


def test_상태별_개수를_센다(task_service: TaskService, task_group_repository) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    t1 = task_service.create(task_group_id=task_group.id, name="A")
    task_service.create(task_group_id=task_group.id, name="B")
    task_service.change_status(t1.id, TaskStatus.DONE)

    counts = task_service.count_by_status(task_group.id)

    assert counts[TaskStatus.DONE] == 1
    assert counts[TaskStatus.PENDING] == 1


def test_삭제하면_담당자와_선행관계도_함께_지워진다(
    task_service: TaskService,
    task_group_repository,
    assignee_repository,
    dependency_repository,
    person_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    a = task_service.create(task_group_id=task_group.id, name="A")
    b = task_service.create(task_group_id=task_group.id, name="B")
    from domain.person import Person

    person = person_repository.add(
        Person(id=None, category=Scope.COMPANY, name="홍주영")
    )
    assignee_repository.add(a.id, person.id)
    dependency_repository.add(a.id, b.id)  # a → b
    dependency_repository.add(b.id, a.id)  # b → a (양방향 삭제 확인용)

    task_service.delete(a.id)

    assert not assignee_repository.exists(a.id, person.id)
    assert not dependency_repository.exists(a.id, b.id)
    assert not dependency_repository.exists(
        b.id, a.id
    )  # depends_on_task_id 쪽도 지워짐


def test_삭제하면_미팅_연결도_함께_지워진다(
    task_service: TaskService,
    task_group_repository,
    meeting_repository,
    meeting_task_repository,
) -> None:
    from datetime import datetime, timezone

    from domain.meeting import Meeting

    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    meeting = meeting_repository.add(
        Meeting(
            id=None,
            task_group_id=task_group.id,
            scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
        )
    )
    meeting_task_repository.add(meeting.id, task.id)

    task_service.delete(task.id)

    assert not meeting_task_repository.exists(meeting.id, task.id)


def test_일반_필드를_수정한다(task_service: TaskService, task_group_repository) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="원래 이름")

    updated = task_service.update(task.id, name="바뀐 이름", estimated_days=3)

    assert updated.name == "바뀐 이름"
    assert updated.estimated_days == 3


def test_같은_상태로_바꾸면_아무일도_안_일어난다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")

    task_service.change_status(task.id, task.status)

    logs = task_service.list_activity_log(task.id)
    assert len(logs) == 1  # 등록 이벤트만 있고, 상태 변경 이벤트는 추가로 안 남음


def test_시작일과_예상소요일만_주면_마감일이_자동으로_채워진다(
    task_service: TaskService, task_group_repository
) -> None:
    """스토리보드 SCENE 02: 08-18(화) + 2일 -> 08-19(수)."""
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )

    task = task_service.create(
        task_group_id=task_group.id,
        name="작업",
        estimated_days=2,
        start_date=date(2026, 8, 18),
    )

    assert task.due_date == date(2026, 8, 19)


def test_공휴일은_영업일에서_빼고_마감일을_계산한다(
    task_service: TaskService, task_group_repository, holiday_calendar_port
) -> None:
    """08-14(금)이 1일째, 주말과 광복절 대체휴일(08-17 월)을 건너뛰어
    08-18(화)이 2일째가 된다."""
    holiday_calendar_port.holidays.add(date(2026, 8, 17))
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )

    task = task_service.create(
        task_group_id=task_group.id,
        name="작업",
        estimated_days=2,
        start_date=date(2026, 8, 14),
    )

    assert task.due_date == date(2026, 8, 18)


def test_마감일을_직접_주면_자동_계산하지_않는다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )

    task = task_service.create(
        task_group_id=task_group.id,
        name="작업",
        estimated_days=2,
        start_date=date(2026, 8, 18),
        due_date=date(2026, 12, 31),
    )

    assert task.due_date == date(2026, 12, 31)


def test_시작일이_없으면_마감일도_비워둔다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )

    task = task_service.create(
        task_group_id=task_group.id, name="작업", estimated_days=5
    )

    assert task.due_date is None


def test_일정_변경시_마감일을_비우면_기존_예상소요일로_계산해_이력에_남긴다(
    task_service: TaskService, task_group_repository
) -> None:
    """초판 구현에서 계산 결과가 버려지던 자리라 이력까지 함께 확인한다."""
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(
        task_group_id=task_group.id, name="작업", estimated_days=2
    )

    updated = task_service.change_schedule(
        task.id, start_date=date(2026, 8, 18), due_date=None
    )

    assert updated.due_date == date(2026, 8, 19)
    logs = task_service.list_activity_log(task.id)
    assert logs[-1].new_value == "2026-08-18 ~ 2026-08-19"


def test_일정_변경시_새_예상소요일을_보내면_그걸_저장하고_마감일_계산에_쓴다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(
        task_group_id=task_group.id, name="작업", estimated_days=2
    )

    updated = task_service.change_schedule(
        task.id, start_date=date(2026, 8, 18), due_date=None, estimated_days=4
    )

    assert updated.estimated_days == 4
    assert updated.due_date == date(2026, 8, 21)


def test_일정_변경시_예상소요일을_생략하면_기존_값을_그대로_쓴다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(
        task_group_id=task_group.id, name="작업", estimated_days=2
    )

    updated = task_service.change_schedule(
        task.id, start_date=date(2026, 8, 18), due_date=None
    )

    assert updated.estimated_days == 2


def test_일정_변경의_마감일_자동계산도_공휴일을_뺀다(
    task_service: TaskService, task_group_repository, holiday_calendar_port
) -> None:
    """create()와 같은 _resolve_due_date를 타므로 일정 변경에서도
    광복절 대체휴일(08-17 월)을 건너뛰는지 직접 확인한다."""
    holiday_calendar_port.holidays.add(date(2026, 8, 17))
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")

    updated = task_service.change_schedule(
        task.id, start_date=date(2026, 8, 14), due_date=None, estimated_days=2
    )

    assert updated.due_date == date(2026, 8, 18)


def test_여러_TaskGroup의_상태별_개수를_한번에_센다(
    task_service: TaskService, task_group_repository
) -> None:
    group_a = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="A")
    )
    group_b = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="B")
    )
    empty = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="비어있음")
    )
    task_a = task_service.create(task_group_id=group_a.id, name="a1")
    task_service.change_status(task_a.id, TaskStatus.DONE)
    task_service.create(task_group_id=group_a.id, name="a2")
    task_service.create(task_group_id=group_b.id, name="b1")

    counts = task_service.count_by_status_bulk([group_a.id, group_b.id, empty.id])

    assert counts[group_a.id] == {TaskStatus.DONE: 1, TaskStatus.PENDING: 1}
    assert counts[group_b.id] == {TaskStatus.PENDING: 1}
    # Task가 하나도 없는 TaskGroup은 키 자체가 없다 — 라우터가 .get(id, {})로 받는다
    assert empty.id not in counts


def test_빈_목록으로_묶음_집계하면_빈_결과(task_service: TaskService) -> None:
    assert task_service.count_by_status_bulk([]) == {}


def test_한달_지나_등록된_보류는_기본_목록에서_빠진다(
    task_service: TaskService, task_group_repository, task_repository
) -> None:
    """도메인에 created_at이 생기기 전에는 Fake가 이 규칙을 흉내 내지
    못해 쓸 수 없던 테스트다."""
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    recent = task_service.create(task_group_id=task_group.id, name="최근 보류")
    old = task_service.create(task_group_id=task_group.id, name="오래된 보류")
    task_repository.get(old.id).created_at = datetime.now(timezone.utc) - timedelta(
        days=31
    )

    default_names = {t.name for t in task_service.list(task_group.id)}
    all_names = {t.name for t in task_service.list(task_group.id, view="all")}

    assert default_names == {recent.name}
    assert all_names == {recent.name, old.name}

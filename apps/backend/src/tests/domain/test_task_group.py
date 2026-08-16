"""TaskGroup 도메인 모델의 검증 규칙을 확인한다."""

from __future__ import annotations

import pytest

from domain.common.enums import Scope
from domain.common.exceptions import EmptyFieldError
from domain.task_group import TaskGroup


def test_이름이_비어있으면_예외() -> None:
    with pytest.raises(EmptyFieldError):
        TaskGroup(id=None, category=Scope.COMPANY, name="   ")

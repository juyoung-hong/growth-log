"""TaskComment 도메인 모델의 검증 규칙을 확인한다."""

from __future__ import annotations

import pytest

from domain.common.exceptions import EmptyFieldError
from domain.task_comment import TaskComment


def test_내용이_비어있으면_예외() -> None:
    with pytest.raises(EmptyFieldError):
        TaskComment(id=None, task_id=1, content="   ")

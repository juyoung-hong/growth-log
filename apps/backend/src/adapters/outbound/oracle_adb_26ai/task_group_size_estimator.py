"""TaskGroupSizeEstimator의 Oracle 구현체.

삭제될 텍스트 콘텐츠의 실제 바이트 수를 LENGTHB()로 직접 잰다.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlmodel import Session

from application.ports.outbound.task_group_size_estimator import TaskGroupSizeEstimator

_QUERY = text(
    """
    SELECT
        NVL((SELECT DBMS_LOB.GETLENGTH(description) FROM task_group WHERE id = :tgid), 0)
      + NVL((SELECT SUM(LENGTHB(name)) FROM task WHERE task_group_id = :tgid), 0)
      + NVL((SELECT SUM(DBMS_LOB.GETLENGTH(c.content)) FROM task_comment c
             JOIN task t ON t.id = c.task_id WHERE t.task_group_id = :tgid), 0)
      + NVL((SELECT SUM(NVL(LENGTHB(l.old_value), 0) + NVL(LENGTHB(l.new_value), 0)
                     + NVL(LENGTHB(l.reason), 0))
             FROM task_activity_log l
             JOIN task t ON t.id = l.task_id WHERE t.task_group_id = :tgid), 0)
      + NVL((SELECT SUM(NVL(DBMS_LOB.GETLENGTH(agenda), 0) + NVL(DBMS_LOB.GETLENGTH(content), 0))
             FROM meeting WHERE task_group_id = :tgid), 0)
    AS total_bytes
    FROM dual
    """
)


class SqlTaskGroupSizeEstimator(TaskGroupSizeEstimator):
    def __init__(self, session: Session):
        self.session = session

    def estimate_content_bytes(self, task_group_id: int) -> int:
        result = self.session.execute(_QUERY, {"tgid": task_group_id}).scalar()
        return int(result or 0)

"""Task 댓글 유스케이스."""

from __future__ import annotations

from application.ports.outbound.task_comment_repository import TaskCommentRepository
from application.ports.outbound.task_repository import TaskRepository
from domain.common.validators import validate_not_empty
from domain.exceptions import TaskCommentNotFoundError, TaskNotFoundError
from domain.task_comment import TaskComment


class TaskCommentService:
    """댓글 등록·조회·수정·삭제 유스케이스."""

    def __init__(
        self,
        comment_repository: TaskCommentRepository,
        task_repository: TaskRepository,
    ) -> None:
        self.comment_repository = comment_repository
        self.task_repository = task_repository

    def list(self, task_id: int) -> list[TaskComment]:
        self._ensure_task_exists(task_id)
        return self.comment_repository.list(task_id)

    def create(self, task_id: int, content: str) -> TaskComment:
        self._ensure_task_exists(task_id)
        comment = TaskComment(id=None, task_id=task_id, content=content)
        return self.comment_repository.add(comment)

    def update(self, comment_id: int, content: str) -> TaskComment:
        """내용을 덮어쓴다. 이력·수정됨 표시는 안 남긴다(Person/TaskGroup과
        동일 원칙). mutate 전에 validate_not_empty를 직접 호출하는 이유는
        TaskService.change_schedule과 같다 — setattr은 __post_init__을
        다시 안 돌린다."""
        validate_not_empty(content, field="content")
        comment = self._get(comment_id)
        comment.content = content
        return self.comment_repository.update(comment)

    def delete(self, comment_id: int) -> None:
        self._get(comment_id)
        self.comment_repository.delete(comment_id)

    def _ensure_task_exists(self, task_id: int) -> None:
        if not self.task_repository.get(task_id):
            raise TaskNotFoundError(task_id)

    def _get(self, comment_id: int) -> TaskComment:
        comment = self.comment_repository.get(comment_id)
        if not comment:
            raise TaskCommentNotFoundError(comment_id)
        return comment

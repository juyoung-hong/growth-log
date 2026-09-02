import type { TaskRead, TaskStatus } from '@/shared/api'
import { request } from '@/shared/api'

/**
 * 완료 체크 전용 엔드포인트. boolean이 아니라 TaskStatus 값을 통째로
 * 보낸다 — `is_done` 같은 필드는 없다. `완료`로 바뀌면 completed_at을
 * 서버가 자동으로 채운다(TaskService.change_status).
 */
export function updateTaskStatus(taskId: number, status: TaskStatus): Promise<TaskRead> {
  return request<TaskRead>(`/tasks/${taskId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  })
}
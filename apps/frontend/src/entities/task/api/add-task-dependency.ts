import type { TaskRead } from '@/shared/api'
import { request } from '@/shared/api'

/** 선행 태스크는 반드시 같은 TaskGroup 소속이어야 한다 — 다르면 서버가 422를 낸다. */
export function addTaskDependency(taskId: number, dependsOnTaskId: number): Promise<TaskRead> {
  return request<TaskRead>(`/tasks/${taskId}/dependencies`, {
    method: 'POST',
    body: JSON.stringify({ depends_on_task_id: dependsOnTaskId }),
  })
}
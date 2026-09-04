import type { TaskRead } from '@/shared/api'
import { request } from '@/shared/api'

export function listTaskDependencies(taskId: number): Promise<TaskRead[]> {
  return request<TaskRead[]>(`/tasks/${taskId}/dependencies`)
}
import type { TaskActivityLogRead } from '@/shared/api'
import { request } from '@/shared/api'

export function listTaskActivityLog(taskId: number): Promise<TaskActivityLogRead[]> {
  return request<TaskActivityLogRead[]>(`/tasks/${taskId}/activity-log`)
}
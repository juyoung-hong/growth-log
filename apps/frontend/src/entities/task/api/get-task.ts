import type { TaskRead } from '@/shared/api'
import { request } from '@/shared/api'

export function getTask(id: number): Promise<TaskRead> {
  return request<TaskRead>(`/tasks/${id}`)
}
import type { TaskGroupRead } from '@/shared/api'
import { request } from '@/shared/api'

export function getTaskGroup(id: number): Promise<TaskGroupRead> {
  return request<TaskGroupRead>(`/task-groups/${id}`)
}
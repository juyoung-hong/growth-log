import type { TaskGroupRead, TaskGroupUpdate } from '@/shared/api'
import { request } from '@/shared/api'

export function updateTaskGroup(id: number, input: TaskGroupUpdate): Promise<TaskGroupRead> {
  return request<TaskGroupRead>(`/task-groups/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}
import type { TaskCreate, TaskRead } from '@/shared/api'
import { request } from '@/shared/api'

export function createTask(taskGroupId: number, input: TaskCreate): Promise<TaskRead> {
  return request<TaskRead>(`/task-groups/${taskGroupId}/tasks`, {
    method: 'POST',
    body: JSON.stringify(input),
  })
}
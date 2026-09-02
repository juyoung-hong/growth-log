import type { TaskGroupCreate, TaskGroupRead } from '@/shared/api'
import { request } from '@/shared/api'

export function createTaskGroup(input: TaskGroupCreate): Promise<TaskGroupRead> {
  return request<TaskGroupRead>('/task-groups', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}
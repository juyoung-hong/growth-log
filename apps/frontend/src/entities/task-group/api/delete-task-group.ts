import { request } from '@/shared/api'

export function deleteTaskGroup(id: number): Promise<void> {
  return request<void>(`/task-groups/${id}`, { method: 'DELETE' })
}
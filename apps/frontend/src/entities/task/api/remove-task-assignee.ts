import { request } from '@/shared/api'

export function removeTaskAssignee(taskId: number, personId: number): Promise<void> {
  return request<void>(`/tasks/${taskId}/assignees/${personId}`, { method: 'DELETE' })
}
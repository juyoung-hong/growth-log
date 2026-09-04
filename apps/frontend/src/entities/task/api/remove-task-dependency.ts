import { request } from '@/shared/api'

export function removeTaskDependency(taskId: number, dependsOnTaskId: number): Promise<void> {
  return request<void>(`/tasks/${taskId}/dependencies/${dependsOnTaskId}`, { method: 'DELETE' })
}
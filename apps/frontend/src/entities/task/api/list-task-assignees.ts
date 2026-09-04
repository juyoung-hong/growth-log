import type { PersonRead } from '@/shared/api'
import { request } from '@/shared/api'

export function listTaskAssignees(taskId: number): Promise<PersonRead[]> {
  return request<PersonRead[]>(`/tasks/${taskId}/assignees`)
}
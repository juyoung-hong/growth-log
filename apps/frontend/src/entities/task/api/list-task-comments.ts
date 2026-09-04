import type { TaskCommentRead } from '@/shared/api'
import { request } from '@/shared/api'

export function listTaskComments(taskId: number): Promise<TaskCommentRead[]> {
  return request<TaskCommentRead[]>(`/tasks/${taskId}/comments`)
}
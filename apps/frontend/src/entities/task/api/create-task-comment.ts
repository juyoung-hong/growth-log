import type { TaskCommentCreate, TaskCommentRead } from '@/shared/api'
import { request } from '@/shared/api'

export function createTaskComment(taskId: number, input: TaskCommentCreate): Promise<TaskCommentRead> {
  return request<TaskCommentRead>(`/tasks/${taskId}/comments`, {
    method: 'POST',
    body: JSON.stringify(input),
  })
}
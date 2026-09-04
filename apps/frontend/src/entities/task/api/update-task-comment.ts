import type { TaskCommentRead, TaskCommentUpdate } from '@/shared/api'
import { request } from '@/shared/api'

export function updateTaskComment(commentId: number, input: TaskCommentUpdate): Promise<TaskCommentRead> {
  return request<TaskCommentRead>(`/comments/${commentId}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}
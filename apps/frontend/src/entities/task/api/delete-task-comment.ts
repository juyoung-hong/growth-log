import { request } from '@/shared/api'

export function deleteTaskComment(commentId: number): Promise<void> {
  return request<void>(`/comments/${commentId}`, { method: 'DELETE' })
}
import type { PersonRead } from '@/shared/api'
import { request } from '@/shared/api'

/** 이미 만들어진 Person만 담당자로 붙일 수 있다 — 즉석 등록은 안 된다. */
export function addTaskAssignee(taskId: number, personId: number): Promise<PersonRead> {
  return request<PersonRead>(`/tasks/${taskId}/assignees`, {
    method: 'POST',
    body: JSON.stringify({ person_id: personId }),
  })
}
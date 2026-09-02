import type { TaskRead } from '@/shared/api'
import { request } from '@/shared/api'

/**
 * 백엔드 라우터 자체는 view를 느슨한 string으로 받는다(서비스 계층의
 * Literal["default", "all"]이 라우터까지 안 내려와 있다) — 그래서 생성된
 * TS 타입도 `view?: string`이다. 오타(`view=ale` 등)를 타입이 못 잡아주므로
 * 프론트에서 이 두 값으로 직접 제한한다.
 */
export type TaskListView = 'default' | 'all'

export function listTasks(taskGroupId: number, view: TaskListView = 'default'): Promise<TaskRead[]> {
  return request<TaskRead[]>(`/task-groups/${taskGroupId}/tasks?view=${view}`)
}
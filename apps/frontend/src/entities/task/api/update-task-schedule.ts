import type { TaskRead, TaskScheduleUpdate } from '@/shared/api'
import { request } from '@/shared/api'

/**
 * 부분 수정이 아니다 — start_date·due_date는 요청에 없으면 서버가
 * null로 간주해 그대로 덮어쓴다(TaskService.change_schedule). 호출하는
 * 쪽이 항상 두 필드를 함께 채워 보내야 한다.
 */
export function updateTaskSchedule(taskId: number, input: TaskScheduleUpdate): Promise<TaskRead> {
  return request<TaskRead>(`/tasks/${taskId}/schedule`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}
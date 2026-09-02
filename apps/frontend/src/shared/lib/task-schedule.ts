import type { TaskRead } from '@/shared/api'

/** 'YYYY-MM-DD' -> 'MM-DD'. 연도는 화면에 안 보여준다 — 프로젝트 하나의
 * 일정이 보통 몇 달 안쪽이라 굳이 자리를 차지할 필요가 없다. */
function toMonthDay(iso: string): string {
  return iso.slice(5)
}

/**
 * 할일목록 한 줄에 보여줄 일정 요약. estimated_days·start_date·due_date는
 * 셋 다 선택값이라 있는 것만 이어 붙인다 — 담당자는 이번 단계 범위 밖이라
 * (Phase 6) 넣지 않는다.
 */
export function formatTaskSchedule(task: Pick<TaskRead, 'estimated_days' | 'start_date' | 'due_date'>): string {
  const parts: string[] = []

  if (task.estimated_days != null) parts.push(`예상 ${task.estimated_days}일`)

  if (task.start_date && task.due_date) parts.push(`${toMonthDay(task.start_date)}~${toMonthDay(task.due_date)}`)
  else if (task.start_date) parts.push(`${toMonthDay(task.start_date)}~`)
  else if (task.due_date) parts.push(`~${toMonthDay(task.due_date)}`)

  return parts.join(' · ') || '일정 미정'
}
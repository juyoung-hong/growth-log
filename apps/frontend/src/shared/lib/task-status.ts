import type { BadgeVariants } from '@/shared/ui/badge'
import type { TaskStatus } from '@/shared/api'

/**
 * TaskStatus는 TaskGroup(레벨2)과 Task(레벨3)가 공유하는 값이다
 * (domain/common/enums.py). scope.ts의 SCOPE_BADGE_COLOR와 같은 이유로
 * shared/lib에 둔다 — 엔티티 하나에 종속된 개념이 아니다.
 *
 * 선언 순서(보류 -> 진행중 -> 완료)가 실제 업무 흐름 순서와 같다.
 * 상태 선택 UI(Tabs 등)를 이 배열로 그리면 항상 자연스러운 순서가 된다.
 */
export const TASK_STATUSES = ['보류', '진행중', '완료'] as const satisfies readonly TaskStatus[]

export const TASK_STATUS_BADGE_COLOR: Record<TaskStatus, NonNullable<BadgeVariants['color']>> = {
  '보류': 'yellow',
  '진행중': 'blue',
  '완료': 'green',
}
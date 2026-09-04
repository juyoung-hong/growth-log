import type { TaskActivityLogRead } from '@/shared/api'

const EVENT_LABELS: Record<string, string> = {
  '등록': '등록됨',
  '상태': '상태 변경',
  '담당자': '담당자 변경',
  '일정': '일정 변경',
  '완료': '완료 처리',
}

/**
 * TaskActivityLogRead.event_type은 ActivityEventType enum이 아니라
 * plain string으로 선언돼 있다(view 파라미터와 같은 패턴) — 알 수 없는
 * 값이 와도 라벨 매핑 없이 원문 그대로 보여주는 정도로만 방어한다.
 *
 * old_value·new_value는 상태 변경이면 "보류"·"진행중" 같은 값 자체,
 * 일정 변경이면 이미 포맷된 "2026-08-18 ~ 2026-08-21" 문자열이다(백엔드
 * TaskService._format_schedule이 만든다) — 프론트가 다시 조합하지 않고
 * 그대로 이어 붙인다. 등록 이벤트는 둘 다 없어 변경 구간 없이 라벨만 남는다.
 */
export function formatActivityEvent(log: Pick<TaskActivityLogRead, 'event_type' | 'old_value' | 'new_value' | 'reason'>): string {
  const label = EVENT_LABELS[log.event_type] ?? log.event_type
  const change = log.old_value != null && log.new_value != null
    ? `${log.old_value} → ${log.new_value}`
    : ''
  const reason = log.reason ? ` (사유: ${log.reason})` : ''
  return change ? `${label}: ${change}${reason}` : `${label}${reason}`
}
import type { TaskActivityLogRead } from '@/shared/api'

const EVENT_LABELS: Record<string, string> = {
  '등록': '등록됨',
  '상태': '상태 변경',
  '담당자': '담당자 변경',
  '일정': '일정 변경',
  '완료': '완료 처리',
  '선행': '선행 관계 변경',
}

/**
 * TaskActivityLogRead.event_type은 ActivityEventType enum이 아니라
 * plain string으로 선언돼 있다(view 파라미터와 같은 패턴) — 알 수 없는
 * 값이 와도 라벨 매핑 없이 원문 그대로 보여주는 정도로만 방어한다.
 *
 * old_value·new_value는 상태·일정 변경이면 "보류"·"진행중"이나 이미
 * 포맷된 "2026-08-18 ~ 2026-08-21" 문자열(백엔드 TaskService._format_schedule이
 * 만든다)이라 "이전값 → 새값"으로 보여준다. 담당자·선행 관계 변경은
 * old_value 없이 new_value만 "홍주영 추가"·"B 제거"처럼 완결된 문장으로
 * 온다(TaskAssigneeService·TaskDependencyService) — 화살표 없이 그대로
 * 보여준다. 등록 이벤트는 둘 다 없어 라벨만 남는다.
 */
export function formatActivityEvent(log: Pick<TaskActivityLogRead, 'event_type' | 'old_value' | 'new_value' | 'reason'>): string {
  const label = EVENT_LABELS[log.event_type] ?? log.event_type
  const reason = log.reason ? ` (사유: ${log.reason})` : ''
  const detail = log.old_value != null && log.new_value != null
    ? `${log.old_value} → ${log.new_value}`
    : log.new_value ?? ''
  return detail ? `${label}: ${detail}${reason}` : `${label}${reason}`
}
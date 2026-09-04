import { describe, expect, it } from 'vitest'
import { formatActivityEvent } from '../task-activity-log'

describe('formatActivityEvent', () => {
  it('등록 이벤트는 변경 구간 없이 라벨만 보여준다', () => {
    expect(formatActivityEvent({ event_type: '등록', old_value: null, new_value: null, reason: null })).toBe('등록됨')
  })

  it('상태 변경은 이전값 → 새값을 함께 보여준다', () => {
    expect(formatActivityEvent({
      event_type: '상태',
      old_value: '보류',
      new_value: '진행중',
      reason: null,
    })).toBe('상태 변경: 보류 → 진행중')
  })

  it('일정 변경에 사유가 있으면 괄호로 덧붙인다', () => {
    expect(formatActivityEvent({
      event_type: '일정',
      old_value: '2026-08-18 ~ 2026-08-21',
      new_value: '2026-08-18 ~ 2026-08-25',
      reason: '담당자 휴가로 순연',
    })).toBe('일정 변경: 2026-08-18 ~ 2026-08-21 → 2026-08-18 ~ 2026-08-25 (사유: 담당자 휴가로 순연)')
  })

  it('알 수 없는 event_type이면 라벨 매핑 없이 원문을 그대로 보여준다', () => {
    expect(formatActivityEvent({ event_type: '보관', old_value: null, new_value: null, reason: null })).toBe('보관')
  })

  it('담당자 변경은 old_value 없이 new_value만 이어 붙인다', () => {
    expect(formatActivityEvent({
      event_type: '담당자',
      old_value: null,
      new_value: '홍주영 추가',
      reason: null,
    })).toBe('담당자 변경: 홍주영 추가')
  })

  it('선행 관계 변경은 old_value 없이 new_value만 이어 붙인다', () => {
    expect(formatActivityEvent({
      event_type: '선행',
      old_value: null,
      new_value: 'DNS 등록 대기 제거',
      reason: null,
    })).toBe('선행 관계 변경: DNS 등록 대기 제거')
  })
})
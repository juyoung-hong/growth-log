import { describe, expect, it } from 'vitest'
import { formatTaskSchedule } from '../task-schedule'

describe('formatTaskSchedule', () => {
  it('예상 소요일과 시작~마감일을 함께 보여준다', () => {
    expect(formatTaskSchedule({
      estimated_days: 4,
      start_date: '2026-08-18',
      due_date: '2026-08-21',
    })).toBe('예상 4일 · 08-18~08-21')
  })

  it('시작일만 있으면 마감일 없이 물결표만 붙인다', () => {
    expect(formatTaskSchedule({
      estimated_days: null,
      start_date: '2026-08-18',
      due_date: null,
    })).toBe('08-18~')
  })

  it('마감일만 있으면 앞에 물결표를 붙인다', () => {
    expect(formatTaskSchedule({
      estimated_days: null,
      start_date: null,
      due_date: '2026-08-21',
    })).toBe('~08-21')
  })

  it('아무 값도 없으면 일정 미정을 보여준다', () => {
    expect(formatTaskSchedule({
      estimated_days: null,
      start_date: null,
      due_date: null,
    })).toBe('일정 미정')
  })
})
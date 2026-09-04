import { describe, expect, it } from 'vitest'
import { formatBytes, formatDateTime } from '../format'

describe('formatBytes', () => {
  it('단위를 1024 기준으로 올린다', () => {
    expect(formatBytes(512)).toBe('512 B')
    expect(formatBytes(1024)).toBe('1.0 KB')
    expect(formatBytes(1024 * 1024)).toBe('1.0 MB')
    expect(formatBytes(20 * 1024 * 1024 * 1024)).toBe('20.0 GB')
  })

  it('세 자리가 되면 소수점을 버린다', () => {
    expect(formatBytes(500 * 1024)).toBe('500 KB')
  })

  it('0과 음수는 0 B로 본다', () => {
    expect(formatBytes(0)).toBe('0 B')
    expect(formatBytes(-1)).toBe('0 B')
  })
})

describe('formatDateTime', () => {
  it('MM-DD HH:mm으로 줄인다 — 로컬(테스트 실행 환경) 시간대 기준', () => {
    // new Date(...).toISOString()으로 UTC 문자열을 만든 뒤 다시
    // formatDateTime에 넣는다 — 그러면 이 테스트도 formatDateTime과
    // 똑같이 로컬 시간대로 되돌려 비교하므로 실행 환경의 시간대가
    // 뭐든 항상 일치한다.
    const local = new Date(2026, 7, 16, 9, 40, 0)
    expect(formatDateTime(local.toISOString())).toBe('08-16 09:40')
  })

  it('한 자리 월·일·시·분은 0을 채운다', () => {
    const local = new Date(2026, 0, 5, 3, 5, 0)
    expect(formatDateTime(local.toISOString())).toBe('01-05 03:05')
  })
})
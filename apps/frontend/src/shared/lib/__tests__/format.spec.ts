import { describe, expect, it } from 'vitest'
import { formatBytes } from '../format'

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
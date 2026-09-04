import { describe, expect, it } from 'vitest'
import { isScopeParam, parseScopeParam, toScope, toScopeParam } from '../scope'

describe('scope 변환', () => {
  it('URL 표기를 API의 한글 값으로 바꾼다', () => {
    expect(toScope('company')).toBe('회사')
    expect(toScope('personal')).toBe('개인')
  })

  it('API의 한글 값을 URL 표기로 바꾼다 — toScope의 반대 방향', () => {
    expect(toScopeParam('회사')).toBe('company')
    expect(toScopeParam('개인')).toBe('personal')
  })

  it('허용된 값만 ScopeParam으로 인정한다', () => {
    expect(isScopeParam('company')).toBe(true)
    expect(isScopeParam('회사')).toBe(false)
    expect(isScopeParam(undefined)).toBe(false)
  })

  it('쿼리 값이 없거나 이상하면 company로 떨어진다', () => {
    // 사용자가 URL을 직접 고쳤을 때 화면이 깨지지 않아야 한다
    expect(parseScopeParam(undefined)).toBe('company')
    expect(parseScopeParam('nonsense')).toBe('company')
    expect(parseScopeParam(['company', 'personal'])).toBe('company')
  })

  it('올바른 쿼리 값은 그대로 통과시킨다', () => {
    expect(parseScopeParam('personal')).toBe('personal')
  })
})
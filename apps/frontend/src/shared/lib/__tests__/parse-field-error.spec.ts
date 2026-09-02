import { describe, expect, it } from 'vitest'
import { parseFieldError } from '../parse-field-error'

describe('parseFieldError', () => {
  it('필드명과 메시지를 분리한다', () => {
    expect(parseFieldError('name: 비어있을 수 없습니다.')).toEqual({
      field: 'name',
      message: '비어있을 수 없습니다.',
    })
  })

  it('밑줄이 든 필드명도 인식한다', () => {
    expect(parseFieldError('some_field: 형식이 올바르지 않습니다.')).toEqual({
      field: 'some_field',
      message: '형식이 올바르지 않습니다.',
    })
  })

  it('필드 접두사가 없으면 null을 반환한다', () => {
    // 이메일 중복(409) 같은 에러는 필드 접두사가 없다 — 호출자가 일반 메시지로 처리해야 한다.
    expect(parseFieldError('일반 에러 메시지입니다.')).toBeNull()
  })
})
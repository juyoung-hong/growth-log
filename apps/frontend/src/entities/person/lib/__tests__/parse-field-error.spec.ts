import { describe, expect, it } from 'vitest'
import { parsePersonFieldError } from '../parse-field-error'

describe('parsePersonFieldError', () => {
  it('name 에러를 필드와 메시지로 분리한다', () => {
    expect(parsePersonFieldError('name: 비어있을 수 없습니다.')).toEqual({
      field: 'name',
      message: '비어있을 수 없습니다.',
    })
  })

  it('email/phone 에러도 같은 형식으로 분리한다', () => {
    expect(parsePersonFieldError('email: 이메일 형식이 올바르지 않습니다: foo')).toEqual({
      field: 'email',
      message: '이메일 형식이 올바르지 않습니다: foo',
    })
    expect(
      parsePersonFieldError('phone: 전화번호는 하이픈을 포함해야 합니다(예: 010-1234-5678): 01012345678'),
    ).toEqual({
      field: 'phone',
      message: '전화번호는 하이픈을 포함해야 합니다(예: 010-1234-5678): 01012345678',
    })
  })

  it('name/email/phone 패턴이 아니면 null을 반환한다', () => {
    // 이메일 중복(409)은 필드 접두사가 없다 — 이 경우 호출자가 일반 메시지로 처리해야 한다.
    expect(parsePersonFieldError('이미 등록된 이메일입니다.')).toBeNull()
    // affiliation·category는 이 패턴에 없는 필드다.
    expect(parsePersonFieldError('affiliation: 비어있을 수 없습니다.')).toBeNull()
  })
})
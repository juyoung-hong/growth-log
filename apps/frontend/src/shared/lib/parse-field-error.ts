const FIELD_PATTERN = /^([a-z_]+): (.+)$/

/**
 * 백엔드 InvalidFieldError 계열(도메인 공용 검증 예외)이 만드는
 * "{field}: {message}" 형식의 400 detail을 필드와 메시지로 쪼갠다.
 *
 * entities/person에서 이 패턴을 처음 다뤘는데, 그때는 필드를
 * 'name' | 'email' | 'phone' 유니언으로 좁혀 반환했다. TaskGroup도
 * 같은 백엔드 규칙을 쓰지만 검증 대상 필드가 name 하나뿐이라 유니언으로
 * 좁힐 이유가 없어서, 여기 shared/lib에는 필드명을 string 그대로
 * 반환하는 범용 버전을 둔다. Person 쪽 전용 버전은 이미 동작하는
 * 코드라 굳이 이걸 쓰도록 바꾸지 않았다.
 */
export function parseFieldError(detail: string): { field: string, message: string } | null {
  const match = FIELD_PATTERN.exec(detail)
  if (!match) return null
  // noUncheckedIndexedAccess 때문에 매치가 성공해도 그룹은 여전히
  // string | undefined다 — 패턴 자체가 두 그룹을 보장하므로 단언한다.
  return { field: match[1]!, message: match[2]! }
}
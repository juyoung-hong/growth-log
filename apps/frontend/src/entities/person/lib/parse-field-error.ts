const FIELD_PATTERN = /^(name|email|phone): (.+)$/

/**
 * 백엔드 400 detail을 필드 단위 에러로 쪼갠다.
 *
 * PersonService가 값 검증에 실패하면 InvalidFieldError를 던지고,
 * API 계층은 str(e)를 그대로 detail에 싣는다. InvalidFieldError의
 * 메시지는 항상 "{field}: {message}" 형태로 만들어지므로 이 패턴으로
 * 원래 필드를 복원할 수 있다.
 *
 * 패턴에 맞지 않으면(예: 다른 원인의 400) null을 반환한다 — 호출자는
 * 이 경우 필드 에러 대신 일반 메시지로 보여줘야 한다.
 */
export function parsePersonFieldError(
  detail: string,
): { field: 'name' | 'email' | 'phone', message: string } | null {
  const match = FIELD_PATTERN.exec(detail)
  if (!match) return null
  // tsconfig의 noUncheckedIndexedAccess 때문에 match[1]/match[2]는
  // 매치가 성공해도 여전히 string | undefined다 — 패턴 자체가 두 그룹을
  // 보장하므로 여기서만 단언한다.
  return { field: match[1] as 'name' | 'email' | 'phone', message: match[2]! }
}
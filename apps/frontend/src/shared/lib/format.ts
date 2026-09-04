const UNITS = ['B', 'KB', 'MB', 'GB', 'TB'] as const

/**
 * 바이트를 사람이 읽는 단위로. 저장공간 게이지에 쓴다.
 *
 * 1024로 나누는 이진 접두사를 쓴다 — OCI 콘솔이 같은 기준으로 표시하기 때문에
 * 화면끼리 숫자가 어긋나지 않는다.
 */
export function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 B'

  let value = bytes
  let unit = 0
  while (value >= 1024 && unit < UNITS.length - 1) {
    value /= 1024
    unit += 1
  }

  // 1 미만 자릿수는 소수점 한 자리까지만 — 게이지 옆 좁은 자리에 들어간다
  const digits = value >= 100 || unit === 0 ? 0 : 1
  return `${value.toFixed(digits)} ${UNITS[unit]}`
}

export function formatDateTime(iso: string): string {
  const date = new Date(iso)
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${month}-${day} ${hour}:${minute}`
}
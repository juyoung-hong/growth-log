const BASE_URL = '/api/v1'

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly detail: string,
  ) {
    super(detail)
  }
}

/** 백엔드 호출 공통 처리. 에러는 ApiError로 통일해서 던진다. */
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })

  if (!response.ok) {
    // FastAPI는 오류를 { "detail": "..." } 형태로 준다
    const body = await response.json().catch(() => null)
    throw new ApiError(response.status, body?.detail ?? response.statusText)
  }

  // 204 No Content(삭제 등)는 본문이 없다
  if (response.status === 204) return undefined as T

  return response.json() as Promise<T>
}
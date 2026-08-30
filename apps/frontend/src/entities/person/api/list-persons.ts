import type { PersonRead, Scope } from '@/shared/api'
import { request } from '@/shared/api'

/** category를 생략하면 회사/개인 전체를 받는다. */
export function listPersons(category?: Scope): Promise<PersonRead[]> {
  const query = category ? `?category=${encodeURIComponent(category)}` : ''
  return request<PersonRead[]>(`/persons${query}`)
}
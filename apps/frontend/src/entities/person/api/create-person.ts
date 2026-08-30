import type { PersonCreate, PersonRead } from '@/shared/api'
import { request } from '@/shared/api'

export function createPerson(input: PersonCreate): Promise<PersonRead> {
  return request<PersonRead>('/persons', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}
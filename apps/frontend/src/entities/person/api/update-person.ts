import type { PersonRead, PersonUpdate } from '@/shared/api'
import { request } from '@/shared/api'

export function updatePerson(id: number, input: PersonUpdate): Promise<PersonRead> {
  return request<PersonRead>(`/persons/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}
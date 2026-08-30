import { request } from '@/shared/api'

export function deletePerson(id: number): Promise<void> {
  return request<void>(`/persons/${id}`, { method: 'DELETE' })
}
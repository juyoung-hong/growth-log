import type { Scope, TaskGroupRead } from '@/shared/api'
import { request } from '@/shared/api'

export interface ListTaskGroupsParams {
  category?: Scope
  /** 기본값(false)이면 보관된 프로젝트는 응답에서 빠진다. */
  includeArchived?: boolean
}

export function listTaskGroups(params: ListTaskGroupsParams = {}): Promise<TaskGroupRead[]> {
  const query = new URLSearchParams()
  if (params.category) query.set('category', params.category)
  if (params.includeArchived) query.set('include_archived', 'true')
  const qs = query.toString()
  return request<TaskGroupRead[]>(`/task-groups${qs ? `?${qs}` : ''}`)
}
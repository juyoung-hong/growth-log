import type { components } from './schema'

type Schemas = components['schemas']

export type PersonRead = Schemas['PersonRead']
export type PersonCreate = Schemas['PersonCreate']
export type PersonUpdate = Schemas['PersonUpdate']

export type TaskGroupRead = Schemas['TaskGroupRead']
export type TaskGroupCreate = Schemas['TaskGroupCreate']
export type TaskGroupUpdate = Schemas['TaskGroupUpdate']
export type TaskGroupProgress = Schemas['TaskGroupProgress']

export type TaskStatus = Schemas['TaskStatus']
export type TaskRead = Schemas['TaskRead']
export type TaskCreate = Schemas['TaskCreate']
export type TaskStatusUpdate = Schemas['TaskStatusUpdate']
export type TaskScheduleUpdate = Schemas['TaskScheduleUpdate']
export type TaskActivityLogRead = Schemas['TaskActivityLogRead']
export type TaskCommentRead = Schemas['TaskCommentRead']
export type TaskCommentCreate = Schemas['TaskCommentCreate']
export type TaskCommentUpdate = Schemas['TaskCommentUpdate']
export type TaskAssigneeAdd = Schemas['TaskAssigneeAdd']
export type TaskDependencyAdd = Schemas['TaskDependencyAdd']

export type Scope = Schemas['Scope']
export type MeetingRead = Schemas['MeetingRead']
export type StorageUsageRead = Schemas['StorageUsageRead']
export type StorageQuota = Schemas['StorageQuota']
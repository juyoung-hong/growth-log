import type { components } from './schema'

type Schemas = components['schemas']

export type Scope = Schemas['Scope']
export type TaskStatus = Schemas['TaskStatus']
export type TaskGroupRead = Schemas['TaskGroupRead']
export type TaskRead = Schemas['TaskRead']
export type PersonRead = Schemas['PersonRead']
export type MeetingRead = Schemas['MeetingRead']
export type StorageUsageRead = Schemas['StorageUsageRead']
export type StorageQuota = Schemas['StorageQuota']
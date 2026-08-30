import type { StorageUsageRead } from '@/shared/api'
import { request } from '@/shared/api'

export function getStorageUsage(): Promise<StorageUsageRead> {
  return request<StorageUsageRead>('/storage/usage')
}
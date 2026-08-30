import type { StorageUsageRead } from '@/shared/api'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getStorageUsage } from '../../api/get-usage'
import { useStorageUsageStore } from '../use-storage-usage'

vi.mock('../../api/get-usage')

const usage: StorageUsageRead = {
  checked_at: '2026-08-30T00:00:00Z',
  db: { used_bytes: 100, limit_bytes: 1000, percent: 10 },
  object_storage: { used_bytes: 0, limit_bytes: 1000, percent: 0 },
  warnings: [],
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.clearAllMocks()
})

describe('useStorageUsageStore', () => {
  it('조회에 성공하면 usage를 채우고 failed는 false로 둔다', async () => {
    vi.mocked(getStorageUsage).mockResolvedValue(usage)
    const store = useStorageUsageStore()

    await store.load()

    expect(store.usage).toEqual(usage)
    expect(store.failed).toBe(false)
    expect(store.loading).toBe(false)
  })

  it('로딩 중에는 loading이 true다', async () => {
    vi.mocked(getStorageUsage).mockResolvedValue(usage)
    const store = useStorageUsageStore()

    const promise = store.load()
    expect(store.loading).toBe(true)
    await promise
    expect(store.loading).toBe(false)
  })

  it('조회에 실패해도 예외를 던지지 않고 게이지만 비운다', async () => {
    vi.mocked(getStorageUsage).mockRejectedValue(new Error('network down'))
    const store = useStorageUsageStore()

    // 게이지는 부가 정보다 — 실패해도 앱이 멈추면 안 되므로 여기서 reject되지 않아야 한다.
    await expect(store.load()).resolves.toBeUndefined()

    expect(store.usage).toBeNull()
    expect(store.failed).toBe(true)
    expect(store.loading).toBe(false)
  })

  it('실패했다가 다시 성공하면 failed가 다시 false로 돌아온다', async () => {
    vi.mocked(getStorageUsage).mockRejectedValueOnce(new Error('network down'))
    const store = useStorageUsageStore()
    await store.load()
    expect(store.failed).toBe(true)

    vi.mocked(getStorageUsage).mockResolvedValueOnce(usage)
    await store.load()

    expect(store.failed).toBe(false)
    expect(store.usage).toEqual(usage)
  })
})

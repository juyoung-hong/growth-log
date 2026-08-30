import type { StorageUsageRead } from '@/shared/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getStorageUsage } from '../api/get-usage'

export const useStorageUsageStore = defineStore('storage-usage', () => {
  const usage = ref<StorageUsageRead | null>(null)
  const loading = ref(false)
  const failed = ref(false)

  async function load() {
    loading.value = true
    failed.value = false
    try {
      usage.value = await getStorageUsage()
    }
    catch {
      // 게이지는 부가 정보다. 조회에 실패해도 앱 전체가 멈추면 안 되므로
      // 예외를 위로 던지지 않고 게이지만 비운다.
      failed.value = true
      usage.value = null
    }
    finally {
      loading.value = false
    }
  }

  return { usage, loading, failed, load }
})
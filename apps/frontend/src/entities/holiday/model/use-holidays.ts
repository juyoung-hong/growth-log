import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listHolidays } from '../api/list-holidays'

/**
 * 연도별로 한 번만 불러와 캐시한다 — 공휴일은 세션 중에 바뀌지 않고,
 * 달력을 쓰는 화면(태스크 등록·일정 변경)마다 같은 연도를 반복해서
 * 조회할 필요가 없다.
 */
export const useHolidaysStore = defineStore('holidays', () => {
  const byYear = ref<Record<number, string[]>>({})
  const loading = ref(false)

  async function ensure(years: number[]) {
    const missing = [...new Set(years)].filter(year => !(year in byYear.value))
    if (missing.length === 0) return
    loading.value = true
    try {
      const results = await Promise.all(missing.map(year => listHolidays(year)))
      for (const [i, year] of missing.entries()) {
        byYear.value[year] = results[i] ?? []
      }
    }
    finally {
      loading.value = false
    }
  }

  return { byYear, loading, ensure }
})

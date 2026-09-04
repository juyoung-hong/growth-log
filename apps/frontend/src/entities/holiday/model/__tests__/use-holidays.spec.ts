import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { listHolidays } from '../../api/list-holidays'
import { useHolidaysStore } from '../use-holidays'

vi.mock('../../api/list-holidays')

beforeEach(() => {
  setActivePinia(createPinia())
  vi.clearAllMocks()
})

describe('useHolidaysStore', () => {
  it('ensure는 연도별로 불러와 채운다', async () => {
    vi.mocked(listHolidays).mockImplementation(async year => [`${year}-01-01`])
    const store = useHolidaysStore()

    await store.ensure([2026, 2027])

    expect(store.byYear[2026]).toEqual(['2026-01-01'])
    expect(store.byYear[2027]).toEqual(['2027-01-01'])
    expect(listHolidays).toHaveBeenCalledTimes(2)
  })

  it('이미 불러온 연도는 다시 조회하지 않는다', async () => {
    vi.mocked(listHolidays).mockResolvedValue(['2026-01-01'])
    const store = useHolidaysStore()
    await store.ensure([2026])

    await store.ensure([2026, 2027])

    expect(listHolidays).toHaveBeenCalledTimes(2) // 2026 한 번 + 2027 한 번
    expect(listHolidays).toHaveBeenCalledWith(2027)
  })

  it('중복된 연도는 한 번만 조회한다', async () => {
    vi.mocked(listHolidays).mockResolvedValue([])
    const store = useHolidaysStore()

    await store.ensure([2026, 2026])

    expect(listHolidays).toHaveBeenCalledTimes(1)
  })
})

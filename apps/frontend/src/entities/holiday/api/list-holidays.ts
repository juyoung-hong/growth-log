import { request } from '@/shared/api'

/** 해당 연도(양력)의 한국 공휴일 날짜를 'YYYY-MM-DD' 문자열로 받는다. */
export function listHolidays(year: number): Promise<string[]> {
  return request<string[]>(`/holidays?year=${year}`)
}

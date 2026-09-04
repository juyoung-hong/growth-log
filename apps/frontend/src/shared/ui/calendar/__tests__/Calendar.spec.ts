import { parseDate } from '@internationalized/date'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import Calendar from '../Calendar.vue'

/**
 * 2026-08 기준: 08-14(금) · 08-15(토, 광복절) · 08-16(일) · 08-17(월,
 * 광복절 대체휴일) · 08-18(화) — Phase B 백엔드 테스트와 같은 달을 쓴다.
 * model-value를 이 달의 날짜로 줘서 캘린더가 8월을 펼친 채로 열리게 한다.
 */
function mountCalendar(props: Record<string, unknown> = {}) {
  return mount(Calendar, {
    props: { modelValue: parseDate('2026-08-18'), ...props },
  })
}

function cell(wrapper: ReturnType<typeof mountCalendar>, date: string) {
  return wrapper.find(`[data-date="${date}"]`)
}

describe('calendar', () => {
  it('토요일은 파란색으로 표기한다', () => {
    const wrapper = mountCalendar()
    expect(cell(wrapper, '2026-08-15').find('span').classes()).toContain('text-blue-600')
  })

  it('일요일은 빨간색으로 표기한다', () => {
    const wrapper = mountCalendar()
    expect(cell(wrapper, '2026-08-16').find('span').classes()).toContain('text-red-600')
  })

  it('평일에 공휴일이 겹치면 빨간색으로 표기한다', () => {
    const wrapper = mountCalendar({ holidays: ['2026-08-17'] }) // 월요일(대체휴일)
    expect(cell(wrapper, '2026-08-17').find('span').classes()).toContain('text-red-600')
  })

  it('공휴일이 토요일과 겹치면 파란색이 아니라 빨간색이 우선한다', () => {
    const wrapper = mountCalendar({ holidays: ['2026-08-15'] }) // 토요일(광복절)
    const classes = cell(wrapper, '2026-08-15').find('span').classes()
    expect(classes).toContain('text-red-600')
    expect(classes).not.toContain('text-blue-600')
  })

  it('평범한 평일은 기본 색으로 표기한다', () => {
    // 08-18(화)은 model-value(선택된 날)라 선택 스타일이 덧씌워진다 —
    // 평일 기본색 확인은 선택되지 않은 다른 평일(08-19, 수)로 본다.
    const wrapper = mountCalendar()
    expect(cell(wrapper, '2026-08-19').find('span').classes()).toContain('text-grey-900')
  })

  it('날짜를 클릭하면 update:modelValue를 그 날짜로 emit한다', async () => {
    const wrapper = mountCalendar()
    await cell(wrapper, '2026-08-20').trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted?.[0]?.[0]?.toString()).toBe('2026-08-20')
  })

  function heading(wrapper: ReturnType<typeof mountCalendar>) {
    return wrapper.find('[data-slot=calendar-heading]')
  }

  it('헤딩을 누르면 월 선택기(1~12월)가 뜨고, 날짜 격자는 사라진다', async () => {
    const wrapper = mountCalendar()
    expect(heading(wrapper).text()).toBe('2026년 8월')

    await heading(wrapper).trigger('click')

    expect(wrapper.find('[data-slot=calendar-month-picker]').exists()).toBe(true)
    expect(cell(wrapper, '2026-08-20').exists()).toBe(false)
    const monthLabels = wrapper.findAll('[data-slot=calendar-month-picker] button').map(b => b.text())
    expect(monthLabels).toEqual(['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'])
  })

  it('월을 고르면 그 달 날짜 격자로 바로 넘어간다', async () => {
    const wrapper = mountCalendar()
    await heading(wrapper).trigger('click')

    const march = wrapper.findAll('[data-slot=calendar-month-picker] button').find(b => b.text() === '3월')
    await march?.trigger('click')

    expect(heading(wrapper).text()).toBe('2026년 3월')
    expect(cell(wrapper, '2026-03-15').exists()).toBe(true)
  })

  it('월 선택기에서 헤딩을 한 번 더 누르면 연도 선택기가 뜬다', async () => {
    const wrapper = mountCalendar()
    await heading(wrapper).trigger('click') // day -> month
    await heading(wrapper).trigger('click') // month -> year

    expect(wrapper.find('[data-slot=calendar-year-picker]').exists()).toBe(true)
    const yearLabels = wrapper.findAll('[data-slot=calendar-year-picker] button').map(b => b.text())
    expect(yearLabels).toHaveLength(12)
    expect(yearLabels).toContain('2026')
  })

  it('연도를 고르면 월 선택기로 돌아가고, 그 연도의 달을 고를 수 있다', async () => {
    const wrapper = mountCalendar()
    await heading(wrapper).trigger('click')
    await heading(wrapper).trigger('click')

    const year2020 = wrapper.findAll('[data-slot=calendar-year-picker] button').find(b => b.text() === '2020')
    await year2020?.trigger('click')

    expect(wrapper.find('[data-slot=calendar-month-picker]').exists()).toBe(true)
    expect(heading(wrapper).text()).toBe('2020년')

    const march = wrapper.findAll('[data-slot=calendar-month-picker] button').find(b => b.text() === '3월')
    await march?.trigger('click')
    expect(cell(wrapper, '2020-03-15').exists()).toBe(true)
  })

  it('월 선택기에서 이전/다음은 한 해씩, 연도 선택기에서는 12년씩 이동한다', async () => {
    const wrapper = mountCalendar()
    await heading(wrapper).trigger('click') // -> month, 2026년

    await wrapper.find('[aria-label=다음]').trigger('click')
    expect(heading(wrapper).text()).toBe('2027년')

    await heading(wrapper).trigger('click') // -> year
    const before = heading(wrapper).text()
    await wrapper.find('[aria-label=다음]').trigger('click')
    const after = heading(wrapper).text()
    expect(after).not.toBe(before)
    // "2016 - 2027" 같은 12년 구간 표기에서 시작 연도가 12 늘어난다.
    const startYearBefore = Number(before.split(' - ')[0])
    const startYearAfter = Number(after.split(' - ')[0])
    expect(startYearAfter - startYearBefore).toBe(12)
  })
})

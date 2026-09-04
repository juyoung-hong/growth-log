import { DOMWrapper, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'
import { nextTick } from 'vue'
import DatePicker from '../DatePicker.vue'

// PopoverContent도 Dialog와 같은 이유로 Teleport로 그려진다 —
// ConfirmDialog.spec.ts와 같은 attachTo + DOMWrapper 패턴을 쓴다.
function mountPicker(props: Record<string, unknown> = {}) {
  const wrapper = mount(DatePicker, {
    attachTo: document.body,
    props: { modelValue: '', label: '시작일', ...props },
  })
  return { wrapper, page: new DOMWrapper(document.body) }
}

describe('datePicker', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  it('값이 없으면 라벨을 자리표시자로 보여준다', () => {
    const { page } = mountPicker()
    expect(page.find('[data-slot=date-picker-trigger]').text()).toBe('시작일')
  })

  it('sustain 라벨에 placeholder도 없이 값이 비면 "날짜 선택"으로 대체한다 — 빈 버튼은 실제 브라우저에서 클릭 영역이 찌그러진다', () => {
    const { page } = mountPicker({ labelOption: 'sustain' })
    expect(page.find('[data-slot=date-picker-trigger]').text()).toBe('날짜 선택')
  })

  it('값이 있으면 그 날짜를 그대로 보여준다', () => {
    const { page } = mountPicker({ modelValue: '2026-08-18' })
    expect(page.find('[data-slot=date-picker-trigger]').text()).toBe('2026-08-18')
  })

  it('트리거를 클릭하면 달력이 열린다', async () => {
    const { page } = mountPicker({ modelValue: '2026-08-18' })
    await page.find('[data-slot=date-picker-trigger]').trigger('click')
    await nextTick()

    expect(page.find('[data-slot=date-picker-content]').exists()).toBe(true)
  })

  it('날짜를 고르면 그 값으로 emit하고 달력을 닫는다', async () => {
    const { wrapper, page } = mountPicker({ modelValue: '2026-08-18' })
    await page.find('[data-slot=date-picker-trigger]').trigger('click')
    await nextTick()

    await page.find('[data-date="2026-08-20"]').trigger('click')
    await nextTick()

    expect(wrapper.emitted('update:modelValue')).toContainEqual(['2026-08-20'])
    expect(page.find('[data-slot=date-picker-content]').exists()).toBe(false)
  })

  it('달력 아이콘을 클릭해도 달력이 열린다 — 아이콘은 트리거 버튼 안에 있다', async () => {
    const { page } = mountPicker()
    await page.find('[data-slot=date-picker-trigger] svg').trigger('click')
    await nextTick()

    expect(page.find('[data-slot=date-picker-content]').exists()).toBe(true)
  })

  it('holidays를 달력에 그대로 전달한다', async () => {
    const { page } = mountPicker({ modelValue: '2026-08-18', holidays: ['2026-08-15'] })
    await page.find('[data-slot=date-picker-trigger]').trigger('click')
    await nextTick()

    expect(page.find('[data-date="2026-08-15"]').find('span').classes()).toContain('text-red-600')
  })

  it('값이 있으면 지우기 버튼이 보이고, 누르면 빈 문자열로 emit한다', async () => {
    const { wrapper, page } = mountPicker({ modelValue: '2026-08-18' })

    await page.find('[aria-label="날짜 지우기"]').trigger('click')

    expect(wrapper.emitted('update:modelValue')).toContainEqual([''])
  })

  it('값이 없으면 지우기 버튼이 보이지 않는다', () => {
    const { page } = mountPicker()
    expect(page.find('[aria-label="날짜 지우기"]').exists()).toBe(false)
  })

  it('달력이 열린 채로 지우기를 누르면 닫히고, 트리거를 다시 누르면 열린다', async () => {
    const { wrapper, page } = mountPicker({ modelValue: '2026-08-18' })

    await page.find('[data-slot=date-picker-trigger]').trigger('click')
    await nextTick()
    expect(page.find('[data-slot=date-picker-content]').exists()).toBe(true)

    await page.find('[aria-label="날짜 지우기"]').trigger('click')
    await wrapper.setProps({ modelValue: '' })
    await nextTick()
    // 지우기가 open을 닫아 두지 않으면, 다음 트리거 클릭이 "열기"가
    // 아니라 "닫기"로 토글돼 달력이 다시 뜨지 않는다(실사용 버그였다).
    expect(page.find('[data-slot=date-picker-content]').exists()).toBe(false)

    await page.find('[data-slot=date-picker-trigger]').trigger('click')
    await nextTick()
    expect(page.find('[data-slot=date-picker-content]').exists()).toBe(true)
  })
})

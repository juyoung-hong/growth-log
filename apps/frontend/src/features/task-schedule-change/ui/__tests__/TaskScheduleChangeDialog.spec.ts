import type { TaskRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { DOMWrapper, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { useTaskDetailStore } from '@/entities/task'
import { ApiError } from '@/shared/api'
import TaskScheduleChangeDialog from '../TaskScheduleChangeDialog.vue'

function task(overrides: Partial<TaskRead> = {}): TaskRead {
  return {
    id: 1, task_group_id: 1, name: '이중화 아키텍처 설계', status: '진행중',
    estimated_days: 4, start_date: '2026-08-18', due_date: '2026-08-21',
    completed_at: null, created_at: '2026-08-16T00:00:00Z', ...overrides,
  }
}

async function mountDialog(t: TaskRead) {
  const wrapper = mount(TaskScheduleChangeDialog, {
    attachTo: document.body,
    props: { open: false, task: t },
    global: { plugins: [createTestingPinia({ stubActions: true, createSpy: vi.fn })] },
  })
  await wrapper.setProps({ open: true })
  await nextTick()
  return { wrapper, page: new DOMWrapper(document.body) }
}

describe('taskScheduleChangeDialog', () => {
  beforeEach(() => { document.body.innerHTML = '' })

  it('열리면 현재 예상소요일·시작일·마감일로 칸을 채운다', async () => {
    const { page } = await mountDialog(task())
    const datePickers = page.findAll('[data-slot=date-picker-trigger]')
    expect(page.findAll('input')[0]?.element.value).toBe('4')
    expect(datePickers[0]?.text()).toBe('2026-08-18')
    expect(datePickers[1]?.text()).toBe('2026-08-21')
  })

  it('예상소요일이 없는 태스크는 빈 칸으로 연다', async () => {
    const { page } = await mountDialog(task({ estimated_days: null }))
    expect(page.findAll('input')[0]?.element.value).toBe('')
  })

  it('저장하면 예상소요일·시작일·마감일·사유를 함께 보낸다', async () => {
    const { page } = await mountDialog(task())
    const store = useTaskDetailStore()
    vi.mocked(store.changeSchedule).mockResolvedValue(undefined as never)

    // 마감일(2026-08-21)이 이미 8월이라 달력을 넘기지 않고도 08-25를 고를 수 있다.
    await page.findAll('[data-slot=date-picker-trigger]')[1]?.trigger('click')
    await nextTick()
    await page.find('[data-date="2026-08-25"]').trigger('click')
    await page.find('textarea').setValue('담당자 휴가로 순연')
    await page.find('form').trigger('submit')
    await nextTick()

    expect(store.changeSchedule).toHaveBeenCalledWith({
      start_date: '2026-08-18', due_date: '2026-08-25', estimated_days: 4, reason: '담당자 휴가로 순연',
    })
  })

  it('마감일을 비운 채 저장하면 null로 보낸다 — 자동 재계산을 서버에 맡긴다', async () => {
    const { page } = await mountDialog(task())
    const store = useTaskDetailStore()
    vi.mocked(store.changeSchedule).mockResolvedValue(undefined as never)

    // 시작일·마감일 둘 다 값이 있어 지우기 버튼이 두 개 뜬다 — 두 번째(마감일)를 누른다.
    await page.findAll('[aria-label="날짜 지우기"]')[1]?.trigger('click')
    await page.find('form').trigger('submit')
    await nextTick()

    expect(store.changeSchedule).toHaveBeenCalledWith(expect.objectContaining({ due_date: null }))
  })

  it('예상소요일을 새로 적고 마감일을 비운 채 저장하면 새 값과 null 마감일을 함께 보낸다 — 서버가 새 소요일로 재계산한다', async () => {
    const { page } = await mountDialog(task())
    const store = useTaskDetailStore()
    vi.mocked(store.changeSchedule).mockResolvedValue(undefined as never)

    await page.findAll('input')[0]?.setValue('7')
    await page.findAll('[aria-label="날짜 지우기"]')[1]?.trigger('click')
    await page.find('form').trigger('submit')
    await nextTick()

    expect(store.changeSchedule).toHaveBeenCalledWith(expect.objectContaining({ estimated_days: 7, due_date: null }))
  })

  it('예상소요일을 비운 채 저장하면 null로 보낸다', async () => {
    const { page } = await mountDialog(task())
    const store = useTaskDetailStore()
    vi.mocked(store.changeSchedule).mockResolvedValue(undefined as never)

    await page.findAll('input')[0]?.setValue('')
    await page.find('form').trigger('submit')
    await nextTick()

    expect(store.changeSchedule).toHaveBeenCalledWith(expect.objectContaining({ estimated_days: null }))
  })

  it('마감일이 시작일보다 빠르다는 400 에러가 오면 마감일 칸에 에러를 건다', async () => {
    const { wrapper, page } = await mountDialog(task())
    const store = useTaskDetailStore()
    vi.mocked(store.changeSchedule).mockRejectedValue(new ApiError(400, 'due_date: 시작일보다 빠를 수 없습니다.'))

    await page.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    expect(page.text()).toContain('시작일보다 빠를 수 없습니다.')
    expect(wrapper.emitted('update:open')).toBeUndefined()
  })
})
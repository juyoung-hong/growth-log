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

  it('열리면 현재 시작일·마감일로 두 칸을 채운다', async () => {
    const { page } = await mountDialog(task())
    const inputs = page.findAll('input')
    expect(inputs[0]?.element.value).toBe('2026-08-18')
    expect(inputs[1]?.element.value).toBe('2026-08-21')
  })

  it('저장하면 시작일·마감일·사유를 함께 보낸다', async () => {
    const { page } = await mountDialog(task())
    const store = useTaskDetailStore()
    vi.mocked(store.changeSchedule).mockResolvedValue(undefined as never)

    const inputs = page.findAll('input')
    await inputs[1]?.setValue('2026-08-25')
    await page.find('textarea').setValue('담당자 휴가로 순연')
    await page.find('form').trigger('submit')
    await nextTick()

    expect(store.changeSchedule).toHaveBeenCalledWith({
      start_date: '2026-08-18', due_date: '2026-08-25', reason: '담당자 휴가로 순연',
    })
  })

  it('마감일을 비운 채 저장하면 null로 보낸다 — 자동 재계산을 서버에 맡긴다', async () => {
    const { page } = await mountDialog(task())
    const store = useTaskDetailStore()
    vi.mocked(store.changeSchedule).mockResolvedValue(undefined as never)

    await page.findAll('input')[1]?.setValue('')
    await page.find('form').trigger('submit')
    await nextTick()

    expect(store.changeSchedule).toHaveBeenCalledWith(expect.objectContaining({ due_date: null }))
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
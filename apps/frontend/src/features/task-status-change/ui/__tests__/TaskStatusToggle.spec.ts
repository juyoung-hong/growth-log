import type { TaskRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { useTaskDetailStore } from '@/entities/task'
import { ApiError } from '@/shared/api'
import TaskStatusToggle from '../TaskStatusToggle.vue'

function task(overrides: Partial<TaskRead> = {}): TaskRead {
  return {
    id: 1, task_group_id: 1, name: '이중화 아키텍처 설계', status: '진행중',
    estimated_days: null, start_date: null, due_date: null,
    completed_at: null, created_at: '2026-08-16T00:00:00Z', ...overrides,
  }
}

function mountToggle(t: TaskRead, dependencies: TaskRead[] = []) {
  const wrapper = mount(TaskStatusToggle, {
    props: { task: t },
    global: {
      plugins: [createTestingPinia({
        stubActions: true,
        createSpy: vi.fn,
        initialState: { 'task-detail': { dependencies } },
      })],
    },
  })
  return { wrapper, store: useTaskDetailStore() }
}

describe('taskStatusToggle', () => {
  it('현재 상태의 항목이 선택된 채로 보인다', () => {
    const { wrapper } = mountToggle(task({ status: '보류' }))
    const selected = wrapper.findAll('[role=radio]').find(r => r.attributes('data-state') === 'checked')
    expect(selected?.text()).toBe('보류')
  })

  it('다른 상태를 클릭하면 changeStatus를 호출한다', async () => {
    const { wrapper, store } = mountToggle(task({ status: '보류' }))
    vi.mocked(store.changeStatus).mockResolvedValue(undefined as never)

    const doneOption = wrapper.findAll('[role=radio]').find(r => r.text() === '완료')
    await doneOption?.trigger('click')

    expect(store.changeStatus).toHaveBeenCalledWith('완료')
  })

  it('지금과 같은 상태를 클릭하면 아무 일도 안 일어난다', async () => {
    const { wrapper, store } = mountToggle(task({ status: '진행중' }))

    const sameOption = wrapper.findAll('[role=radio]').find(r => r.text() === '진행중')
    await sameOption?.trigger('click')

    expect(store.changeStatus).not.toHaveBeenCalled()
  })

  it('실패하면 에러 메시지를 보여준다', async () => {
    const { wrapper, store } = mountToggle(task({ status: '보류' }))
    vi.mocked(store.changeStatus).mockRejectedValue(new ApiError(500, '서버 오류'))

    const doneOption = wrapper.findAll('[role=radio]').find(r => r.text() === '완료')
    await doneOption?.trigger('click')
    await nextTick()
    await nextTick()

    expect(wrapper.text()).toContain('서버 오류')
  })

  it('미완료 선행 태스크가 있으면 완료 항목이 비활성화되고 이유가 보인다', () => {
    const { wrapper } = mountToggle(
      task({ status: '진행중' }),
      [task({ id: 2, name: 'DNS 등록 대기', status: '보류' })],
    )

    const doneOption = wrapper.findAll('[role=radio]').find(r => r.text() === '완료')
    expect(doneOption?.attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('선행 태스크가 모두 끝나야 완료할 수 있습니다: DNS 등록 대기 (보류)')
  })

  it('미완료 선행 태스크가 있어도 완료가 아닌 다른 상태로는 바꿀 수 있다', async () => {
    const { wrapper, store } = mountToggle(
      task({ status: '진행중' }),
      [task({ id: 2, name: 'DNS 등록 대기', status: '보류' })],
    )

    const pendingOption = wrapper.findAll('[role=radio]').find(r => r.text() === '보류')
    await pendingOption?.trigger('click')

    expect(store.changeStatus).toHaveBeenCalledWith('보류')
  })

  it('선행 태스크가 모두 완료면 완료 항목이 다시 활성화된다', () => {
    const { wrapper } = mountToggle(
      task({ status: '진행중' }),
      [task({ id: 2, name: 'DNS 등록', status: '완료' })],
    )

    const doneOption = wrapper.findAll('[role=radio]').find(r => r.text() === '완료')
    expect(doneOption?.attributes('disabled')).toBeUndefined()
  })
})
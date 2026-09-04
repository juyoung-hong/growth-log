import type { TaskRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { useTasksStore } from '@/entities/task'
import { ApiError } from '@/shared/api'
import TaskCompleteCheckbox from '../TaskCompleteCheckbox.vue'

function task(overrides: Partial<TaskRead> = {}): TaskRead {
  return {
    id: 1,
    task_group_id: 1,
    name: '이중화 아키텍처 설계',
    status: '진행중',
    estimated_days: null,
    start_date: null,
    due_date: null,
    completed_at: null,
    created_at: '2026-08-16T00:00:00Z',
    ...overrides,
  }
}

function mountCheckbox(t: TaskRead, blockingDependency?: TaskRead) {
  const wrapper = mount(TaskCompleteCheckbox, {
    props: { task: t, blockingDependency },
    global: {
      plugins: [createTestingPinia({ stubActions: true, createSpy: vi.fn })],
    },
  })
  return { wrapper, store: useTasksStore() }
}

describe('taskCompleteCheckbox', () => {
  it('완료 상태면 체크·비활성화된 채로 보여준다 — 체크 해제로 되돌리는 동작은 이번 단계 범위 밖이다', () => {
    const { wrapper } = mountCheckbox(task({ status: '완료' }))
    const checkbox = wrapper.find('input[type=checkbox]').element as HTMLInputElement
    expect(checkbox.checked).toBe(true)
    expect(checkbox.disabled).toBe(true)
  })

  it('체크하면 낙관적으로 완료 처리한 뒤 완료 API를 호출한다', async () => {
    const { wrapper, store } = mountCheckbox(task({ status: '진행중' }))
    vi.mocked(store.completeTask).mockResolvedValue(undefined as never)

    await wrapper.find('input[type=checkbox]').trigger('change')

    expect(store.setLocalStatus).toHaveBeenCalledWith(1, '완료')
    expect(store.completeTask).toHaveBeenCalledWith(1)
  })

  it('실패하면 이전 상태로 되돌리고 에러 메시지를 보여준다', async () => {
    const { wrapper, store } = mountCheckbox(task({ status: '보류' }))
    vi.mocked(store.completeTask).mockRejectedValue(new ApiError(500, '서버 오류'))

    await wrapper.find('input[type=checkbox]').trigger('change')
    await nextTick()
    await nextTick()

    expect(store.setLocalStatus).toHaveBeenNthCalledWith(1, 1, '완료')
    expect(store.setLocalStatus).toHaveBeenNthCalledWith(2, 1, '보류')
    expect(wrapper.text()).toContain('서버 오류')
  })

  it('미완료 선행 태스크가 있으면 비활성화되고 이유가 title에 보인다', () => {
    const blockingTask = task({ id: 2, name: 'DNS 등록 대기', status: '보류' })
    const { wrapper } = mountCheckbox(task({ status: '진행중' }), blockingTask)

    const checkbox = wrapper.find('input[type=checkbox]').element as HTMLInputElement
    expect(checkbox.disabled).toBe(true)
    expect(checkbox.title).toBe('선행 태스크(DNS 등록 대기)가 끝나야 완료할 수 있습니다.')
  })

  it('미완료 선행 태스크가 있으면 체크해도 completeTask를 호출하지 않는다', async () => {
    const blockingTask = task({ id: 2, name: 'DNS 등록 대기', status: '보류' })
    const { wrapper, store } = mountCheckbox(task({ status: '진행중' }), blockingTask)

    await wrapper.find('input[type=checkbox]').trigger('change')

    expect(store.completeTask).not.toHaveBeenCalled()
  })
})
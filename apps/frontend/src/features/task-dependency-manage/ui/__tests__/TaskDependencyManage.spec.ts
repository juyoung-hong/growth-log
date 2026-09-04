import type { TaskRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { listTasks, useTaskDetailStore } from '@/entities/task'
import { ApiError } from '@/shared/api'
import TaskDependencyManage from '../TaskDependencyManage.vue'

// entities/task의 공개 API(index.ts)만 통해서 mock한다 — steiger가
// 하위 모듈(api/list-tasks) 직접 import를 금지한다(fsd/no-public-api-sidestep).
vi.mock('@/entities/task', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/entities/task')>()
  return { ...actual, listTasks: vi.fn<typeof actual.listTasks>() }
})

function task(overrides: Partial<TaskRead> = {}): TaskRead {
  return {
    id: 1, task_group_id: 1, name: '이중화 아키텍처 설계', status: '진행중',
    estimated_days: null, start_date: null, due_date: null,
    completed_at: null, created_at: '2026-08-16T00:00:00Z', ...overrides,
  }
}

function mountManage(dependencies: TaskRead[] = [], groupTasks: TaskRead[] = []) {
  vi.mocked(listTasks).mockResolvedValue(groupTasks)
  const wrapper = mount(TaskDependencyManage, {
    global: {
      plugins: [
        createTestingPinia({
          stubActions: true,
          createSpy: vi.fn,
          initialState: { 'task-detail': { task: task(), dependencies } },
        }),
      ],
    },
  })
  return { wrapper, taskStore: useTaskDetailStore() }
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('taskDependencyManage', () => {
  it('선행 태스크가 없으면 안내 문구를 보여준다', async () => {
    const { wrapper } = mountManage()
    await nextTick()
    expect(wrapper.text()).toContain('선행 태스크가 없습니다.')
  })

  it('선행 태스크 칩을 상태 배지와 함께 보여주고, 미완료면 ⚠를 붙인다', async () => {
    const { wrapper } = mountManage([task({ id: 2, name: '아키텍처 설계', status: '진행중' })])
    await nextTick()

    expect(wrapper.text()).toContain('아키텍처 설계')
    expect(wrapper.text()).toContain('⚠')
  })

  it('완료된 선행 태스크에는 ⚠를 붙이지 않는다', async () => {
    const { wrapper } = mountManage([task({ id: 2, name: '완료된 설계', status: '완료' })])
    await nextTick()

    expect(wrapper.text()).not.toContain('⚠')
  })

  it('×를 누르면 removeDependency를 호출한다', async () => {
    const { wrapper, taskStore } = mountManage([task({ id: 2, name: '아키텍처 설계' })])
    await nextTick()

    await wrapper.find('button[aria-label="아키텍처 설계 선행 태스크에서 제거"]').trigger('click')
    expect(taskStore.removeDependency).toHaveBeenCalledWith(2)
  })

  it('+ 선행 태스크를 누르면 자기 자신과 이미 선행인 태스크를 뺀 후보가 보인다', async () => {
    const { wrapper } = mountManage(
      [task({ id: 2, name: '아키텍처 설계' })],
      [
        task({ id: 1, name: '이중화 아키텍처 설계' }), // 자기 자신
        task({ id: 2, name: '아키텍처 설계' }), // 이미 선행
        task({ id: 3, name: 'DNS 등록' }),
      ],
    )
    await nextTick()

    await wrapper.findAll('button').find(b => b.text() === '+ 선행 태스크')?.trigger('click')
    await nextTick()

    const candidateNames = wrapper.findAll('li button').map(b => b.text())
    expect(candidateNames.some(t => t.includes('DNS 등록'))).toBe(true)
    expect(candidateNames.some(t => t.includes('이중화 아키텍처 설계'))).toBe(false)
  })

  it('검색어로 후보를 좁힌다', async () => {
    const { wrapper } = mountManage(
      [],
      [task({ id: 2, name: 'DNS 등록' }), task({ id: 3, name: '부하분산 정책 검토' })],
    )
    await nextTick()

    await wrapper.findAll('button').find(b => b.text() === '+ 선행 태스크')?.trigger('click')
    await nextTick()
    await wrapper.find('input').setValue('DNS')

    const candidateNames = wrapper.findAll('li button').map(b => b.text())
    expect(candidateNames.some(t => t.includes('DNS 등록'))).toBe(true)
    expect(candidateNames.some(t => t.includes('부하분산 정책 검토'))).toBe(false)
  })

  it('완료된 태스크는 후보 목록에서 뒤로 밀린다', async () => {
    const { wrapper } = mountManage(
      [],
      [
        task({ id: 2, name: '완료된 작업', status: '완료' }),
        task({ id: 3, name: '진행중 작업', status: '진행중' }),
        task({ id: 4, name: '보류중 작업', status: '보류' }),
      ],
    )
    await nextTick()

    await wrapper.findAll('button').find(b => b.text() === '+ 선행 태스크')?.trigger('click')
    await nextTick()

    const candidateNames = wrapper.findAll('li button').map(b => b.text())
    expect(candidateNames[candidateNames.length - 1]).toContain('완료된 작업')
  })

  it('후보를 클릭하면 addDependency를 호출한다', async () => {
    const { wrapper, taskStore } = mountManage([], [task({ id: 3, name: 'DNS 등록' })])
    await nextTick()

    await wrapper.findAll('button').find(b => b.text() === '+ 선행 태스크')?.trigger('click')
    await nextTick()
    const candidate = wrapper.findAll('li button').find(b => b.text().includes('DNS 등록'))
    await candidate?.trigger('click')

    expect(taskStore.addDependency).toHaveBeenCalledWith(3)
  })

  it('추가에 실패하면 에러 메시지를 보여준다', async () => {
    const { wrapper, taskStore } = mountManage([], [task({ id: 3, name: 'DNS 등록' })])
    vi.mocked(taskStore.addDependency).mockRejectedValue(new ApiError(422, '선행 태스크는 같은 TaskGroup에 속해야 합니다.'))
    await nextTick()

    await wrapper.findAll('button').find(b => b.text() === '+ 선행 태스크')?.trigger('click')
    await nextTick()
    const candidate = wrapper.findAll('li button').find(b => b.text().includes('DNS 등록'))
    await candidate?.trigger('click')
    await nextTick()

    expect(wrapper.text()).toContain('선행 태스크는 같은 TaskGroup에 속해야 합니다.')
  })
})
import type { PersonRead, TaskRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { useTaskDetailStore } from '@/entities/task'
import { usePersonsStore } from '@/entities/person'
import { ApiError } from '@/shared/api'
import TaskAssigneeManage from '../TaskAssigneeManage.vue'

function task(overrides: Partial<TaskRead> = {}): TaskRead {
  return {
    id: 1, task_group_id: 1, name: '이중화 아키텍처 설계', status: '진행중',
    estimated_days: null, start_date: null, due_date: null,
    completed_at: null, created_at: '2026-08-16T00:00:00Z', ...overrides,
  }
}

function person(overrides: Partial<PersonRead> = {}): PersonRead {
  return { id: 1, category: '회사', name: '홍주영', email: null, phone: null, affiliation: null, ...overrides }
}

function mountManage(assignees: PersonRead[] = [], persons: PersonRead[] = []) {
  const wrapper = mount(TaskAssigneeManage, {
    global: {
      plugins: [
        createTestingPinia({
          stubActions: true,
          createSpy: vi.fn,
          initialState: {
            'task-detail': { task: task(), assignees },
            'persons': { persons },
          },
        }),
      ],
    },
  })
  return { wrapper, taskStore: useTaskDetailStore(), personsStore: usePersonsStore() }
}

describe('taskAssigneeManage', () => {
  it('담당자가 없으면 안내 문구를 보여준다', () => {
    const { wrapper } = mountManage()
    expect(wrapper.text()).toContain('아직 담당자가 없습니다.')
  })

  it('담당자 칩을 보여주고, ×를 누르면 removeAssignee를 호출한다', async () => {
    const { wrapper, taskStore } = mountManage([person()])
    expect(wrapper.text()).toContain('홍주영')

    await wrapper.find('button[aria-label="홍주영 담당자에서 제거"]').trigger('click')
    expect(taskStore.removeAssignee).toHaveBeenCalledWith(1)
  })

  it('+ 담당자를 누르면 이미 담당자인 사람을 뺀 후보 목록이 보인다', async () => {
    const { wrapper } = mountManage(
      [person({ id: 1, name: '홍주영' })],
      [person({ id: 1, name: '홍주영' }), person({ id: 2, name: '김도현' })],
    )

    await wrapper.findAll('button').find(b => b.text() === '+ 담당자')?.trigger('click')
    await nextTick()

    const candidateNames = wrapper.findAll('li button').map(b => b.text())
    expect(candidateNames.some(t => t.includes('김도현'))).toBe(true)
    expect(candidateNames.some(t => t.includes('홍주영'))).toBe(false)
  })

  it('후보를 클릭하면 addAssignee를 호출한다', async () => {
    const { wrapper, taskStore } = mountManage([], [person({ id: 2, name: '김도현' })])

    await wrapper.findAll('button').find(b => b.text() === '+ 담당자')?.trigger('click')
    await nextTick()
    const candidate = wrapper.findAll('li button').find(b => b.text().includes('김도현'))
    await candidate?.trigger('click')

    expect(taskStore.addAssignee).toHaveBeenCalledWith(2)
  })

  it('검색어로 후보를 좁힌다', async () => {
    const { wrapper } = mountManage(
      [],
      [person({ id: 1, name: '홍주영' }), person({ id: 2, name: '김도현' })],
    )

    await wrapper.findAll('button').find(b => b.text() === '+ 담당자')?.trigger('click')
    await nextTick()
    await wrapper.find('input').setValue('김')

    expect(wrapper.text()).toContain('김도현')
    expect(wrapper.text()).not.toContain('홍주영')
  })

  it('추가에 실패하면 에러 메시지를 보여준다', async () => {
    const { wrapper, taskStore } = mountManage([], [person({ id: 2, name: '김도현' })])
    vi.mocked(taskStore.addAssignee).mockRejectedValue(new ApiError(404, '인물을 찾을 수 없습니다.'))

    await wrapper.findAll('button').find(b => b.text() === '+ 담당자')?.trigger('click')
    await nextTick()
    const candidate = wrapper.findAll('li button').find(b => b.text().includes('김도현'))
    await candidate?.trigger('click')
    await nextTick()

    expect(wrapper.text()).toContain('인물을 찾을 수 없습니다.')
  })
})
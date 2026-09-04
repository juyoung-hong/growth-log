import type { TaskActivityLogRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import TaskActivityLog from '../TaskActivityLog.vue'

const registered: TaskActivityLogRead = {
  id: 1, event_type: '등록', event_at: '2026-08-16T00:00:00Z',
  old_value: null, new_value: null, reason: null,
}
const statusChanged: TaskActivityLogRead = {
  id: 2, event_type: '상태', event_at: '2026-08-17T00:00:00Z',
  old_value: '보류', new_value: '진행중', reason: null,
}

function mountWidget(activityLog: TaskActivityLogRead[]) {
  return mount(TaskActivityLog, {
    global: {
      plugins: [createTestingPinia({
        stubActions: true, createSpy: vi.fn,
        initialState: { 'task-detail': { activityLog } },
      })],
    },
  })
}

describe('taskActivityLog', () => {
  it('기록이 없으면 안내 문구를 보여준다', () => {
    const wrapper = mountWidget([])
    expect(wrapper.text()).toContain('아직 기록이 없습니다.')
  })

  it('시간순으로 받은 그대로 렌더링한다', () => {
    const wrapper = mountWidget([registered, statusChanged])
    const items = wrapper.findAll('li')
    expect(items).toHaveLength(2)
    expect(items[0]?.text()).toContain('등록됨')
    expect(items[1]?.text()).toContain('상태 변경: 보류 → 진행중')
  })
})
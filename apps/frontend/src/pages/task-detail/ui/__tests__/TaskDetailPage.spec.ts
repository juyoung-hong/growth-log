import type { TaskGroupRead, TaskRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { DOMWrapper, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { getTaskGroup } from '@/entities/task-group'
import TaskDetailPage from '../TaskDetailPage.vue'

// TaskGroupDetailPage.spec.ts와 같은 이유로 RouterLink도 mock에 넣는다.
vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: '1', taskId: '7' } }),
  RouterLink: { props: ['to'], template: '<a :data-to="JSON.stringify(to)"><slot /></a>' },
}))

// getTaskGroup은 store 액션이 아니라 평범한 함수라 createTestingPinia로는
// 못 막는다 — 모듈 자체를 mock한다(TaskGroupDetailPage.spec.ts와 동일).
vi.mock('@/entities/task-group', () => ({
  getTaskGroup: vi.fn<(id: number) => Promise<TaskGroupRead>>(),
}))

const task: TaskRead = {
  id: 7, task_group_id: 1, name: '이중화 아키텍처 설계', status: '진행중',
  estimated_days: 4, start_date: '2026-08-18', due_date: '2026-08-21',
  completed_at: null, created_at: '2026-08-16T00:00:00Z',
}

const taskGroup: TaskGroupRead = {
  id: 1, category: '회사', name: '메일서버 이중화', description: null,
  status: '진행중', is_archived: false, created_at: '2026-08-01T00:00:00Z',
  progress: { total_tasks: 10, done_tasks: 7, percent: 70 },
}

/**
 * TaskGroupDetailPage.spec.ts와 같은 이유로 attachTo + DOMWrapper를 쓴다 —
 * "일정 변경" 버튼이 여는 TaskScheduleChangeDialog가 Teleport로 그려진다.
 *
 * store.task 값이 바뀌는 걸 watch(taskGroupId, ...)가 지켜보다 getTaskGroup을
 * 부르므로, 그 microtask가 끝나길 nextTick으로 기다린다.
 */
async function mountPage() {
  vi.mocked(getTaskGroup).mockResolvedValue(taskGroup)
  const wrapper = mount(TaskDetailPage, {
    attachTo: document.body,
    global: {
      plugins: [createTestingPinia({
        stubActions: true, createSpy: vi.fn,
        initialState: { 'task-detail': { task, activityLog: [], comments: [], loading: false } },
      })],
    },
  })
  await nextTick()
  await nextTick()
  return { wrapper, page: new DOMWrapper(document.body) }
}

describe('taskDetailPage', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
    vi.clearAllMocks()
  })

  it('이름·예상소요일·일정을 보여준다', async () => {
    const { page } = await mountPage()
    expect(page.text()).toContain('이중화 아키텍처 설계')
    expect(page.text()).toContain('예상 4일')
    expect(page.text()).toContain('08-18~08-21')
  })

  it('활동 이력·댓글 위젯을 함께 보여준다', async () => {
    const { page } = await mountPage()
    expect(page.text()).toContain('활동 이력')
    expect(page.text()).toContain('댓글')
  })

  it('"일정 변경" 버튼을 누르면 다이얼로그가 열린다', async () => {
    const { page } = await mountPage()
    const button = page.findAll('button').find(b => b.text() === '일정 변경')
    await button?.trigger('click')
    await nextTick()

    expect(page.find('[data-slot=dialog-title]').text()).toBe('일정 변경')
  })

  it('브레드크럼이 할일관리 › 프로젝트 이름 › 태스크 이름 순서로 보인다', async () => {
    const { page } = await mountPage()
    const links = page.find('nav').findAll('a')

    expect(links[0]?.text()).toBe('할일관리')
    expect(JSON.parse(links[0]?.attributes('data-to') ?? '{}')).toEqual({
      name: 'task-groups',
      query: { scope: 'company' },
    })

    expect(links[1]?.text()).toBe('메일서버 이중화')
    expect(JSON.parse(links[1]?.attributes('data-to') ?? '{}')).toEqual({
      name: 'task-group-detail',
      params: { id: 1 },
    })
  })

  it('브레드크럼의 마지막 조각(지금 태스크)은 링크가 아니라 글자로만 보인다', async () => {
    const { page } = await mountPage()
    const nav = page.find('nav')
    expect(nav.text()).toContain('이중화 아키텍처 설계')
    expect(nav.findAll('a')).toHaveLength(2) // "할일관리"·프로젝트 이름만 링크다
  })
})
import type { TaskGroupRead, TaskRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { DOMWrapper, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { getTaskGroup } from '@/entities/task-group'
import TaskGroupDetailPage from '../TaskGroupDetailPage.vue'

// TaskGroupsPage.spec.ts와 같은 이유로 useRoute를 고정값으로 mock한다.
vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: '1' } }),
}))

// getTaskGroup은 store 액션이 아니라 entities/task-group이 내보내는
// 평범한 함수라 createTestingPinia로는 못 막는다 — 모듈 자체를 mock한다.
vi.mock('@/entities/task-group', () => ({
  getTaskGroup: vi.fn<(id: number) => Promise<TaskGroupRead>>(),
}))

const taskGroup: TaskGroupRead = {
  id: 1,
  category: '회사',
  name: '메일서버 이중화',
  description: '기존 단일 메일서버를 이중화한다',
  status: '진행중',
  is_archived: false,
  created_at: '2026-08-01T00:00:00Z',
  progress: { total_tasks: 10, done_tasks: 7, percent: 70 },
}

function task(overrides: Partial<TaskRead> = {}): TaskRead {
  return {
    id: 1,
    task_group_id: 1,
    name: '이중화 아키텍처 설계',
    status: '진행중',
    estimated_days: 4,
    start_date: '2026-08-18',
    due_date: '2026-08-21',
    completed_at: null,
    created_at: '2026-08-16T00:00:00Z',
    ...overrides,
  }
}

/**
 * PersonFormDialog.spec.ts와 같은 이유로 attachTo + DOMWrapper를 쓴다 —
 * "+ 태스크" 버튼이 여는 TaskFormDialog가 Teleport로 그려진다.
 *
 * watch(taskGroupId, async ..., { immediate: true })가 getTaskGroup →
 * tasksStore.load 순서로 두 번 await하므로, 둘 다 끝나길 nextTick을
 * 몇 번 기다려서 확인한다.
 */
async function mountPage(tasks: TaskRead[] = [], allTasks: TaskRead[] = tasks) {
  vi.mocked(getTaskGroup).mockResolvedValue(taskGroup)
  const wrapper = mount(TaskGroupDetailPage, {
    attachTo: document.body,
    global: {
      plugins: [
        createTestingPinia({
          stubActions: true,
          createSpy: vi.fn,
          initialState: { tasks: { tasks, allTasks, loading: false } },
        }),
      ],
    },
  })
  await nextTick()
  await nextTick()
  await nextTick()
  return { wrapper, page: new DOMWrapper(document.body) }
}

describe('taskGroupDetailPage', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
    vi.clearAllMocks()
  })

  it('헤더에 이름·상태·진행률을 보여준다', async () => {
    const { page } = await mountPage()
    expect(page.text()).toContain('메일서버 이중화')
    expect(page.text()).toContain('진행중')
    expect(page.text()).toContain('7/10 완료')
  })

  it('할일목록 탭엔 기본 필터로 불러온 태스크만 보인다', async () => {
    const { page } = await mountPage(
      [task({ id: 1 })],
      [task({ id: 1 }), task({ id: 2, name: '완료된 태스크', status: '완료' })],
    )
    expect(page.text()).toContain('이중화 아키텍처 설계')
    expect(page.text()).not.toContain('완료된 태스크')
  })

  it('상태별 건수를 보류·진행중·완료로 나눠 보여준다 — allTasks 기준이라 숨겨진 완료도 셈에 든다', async () => {
    const { page } = await mountPage(
      [task({ id: 1, status: '진행중' })],
      [
        task({ id: 1, status: '진행중' }),
        task({ id: 2, status: '보류' }),
        task({ id: 3, status: '완료' }),
      ],
    )
    expect(page.text()).toContain('보류 1건, 진행중 1건, 완료 1건')
  })

  it('전체보기를 누르면 숨겨진 태스크도 보이고, 버튼 문구가 되돌아가기로 바뀐다', async () => {
    const { page } = await mountPage(
      [task({ id: 1 })],
      [task({ id: 1 }), task({ id: 2, name: '완료된 태스크', status: '완료' })],
    )

    const toggleButton = () => page.findAll('button').find(b => b.text() === '전체보기' || b.text() === '기본 보기로 돌아가기')
    await toggleButton()?.trigger('click')

    expect(page.text()).toContain('완료된 태스크')
    expect(toggleButton()?.text()).toBe('기본 보기로 돌아가기')

    await toggleButton()?.trigger('click')

    expect(page.text()).not.toContain('완료된 태스크')
    expect(toggleButton()?.text()).toBe('전체보기')
  })

  it('할일이 없으면 안내 문구를 보여준다', async () => {
    const { page } = await mountPage([])
    expect(page.text()).toContain('등록된 태스크가 없습니다.')
  })

  it('"+ 태스크" 버튼을 누르면 등록 다이얼로그가 열린다', async () => {
    const { page } = await mountPage()
    const createButton = page.findAll('button').find(b => b.text() === '+ 태스크')
    await createButton?.trigger('click')
    await nextTick()

    expect(page.text()).toContain('새 태스크')
  })

  it('회의록·참고자료 탭은 플레이스홀더만 보여준다', async () => {
    const { page } = await mountPage()
    const meetingsTab = page.findAll('[role=tab]').find(t => t.text() === '회의록')
    await meetingsTab?.trigger('focus')

    expect(page.text()).toContain('다음 단계에서 만듭니다.')
  })
})
import type { TaskGroupRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { DOMWrapper, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { useTaskGroupsStore } from '@/entities/task-group'
import TaskGroupsPage from '../TaskGroupsPage.vue'

const { pushMock } = vi.hoisted(() => ({ pushMock: vi.fn<(to: unknown) => void>() }))

// PersonsPage.spec.ts와 같은 이유로 useRoute를 고정값으로 mock한다.
// 이 페이지는 카드 클릭 시 router.push도 직접 부르므로 useRouter도 같이 mock한다.
vi.mock('vue-router', () => ({
  useRoute: () => ({ query: {} }),
  useRouter: () => ({ push: pushMock }),
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

const doneTaskGroup: TaskGroupRead = {
  ...taskGroup,
  id: 2,
  name: '완료된 프로젝트',
  status: '완료',
  progress: { total_tasks: 3, done_tasks: 3, percent: 100 },
}

function mountPage(taskGroups: TaskGroupRead[] = [], loading = false) {
  const wrapper = mount(TaskGroupsPage, {
    attachTo: document.body,
    global: {
      stubs: { ScopeSwitch: true },
      plugins: [
        createTestingPinia({
          stubActions: true,
          createSpy: vi.fn,
          initialState: { 'task-groups': { taskGroups, loading } },
        }),
      ],
    },
  })
  return { wrapper, page: new DOMWrapper(document.body) }
}

describe('taskGroupsPage', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
    pushMock.mockClear()
  })

  it('불러오는 중이면 로딩 문구를 보여준다', () => {
    const { page } = mountPage([], true)
    expect(page.text()).toContain('불러오는 중')
  })

  it('목록이 비어 있으면 안내 문구를 보여준다', () => {
    const { page } = mountPage([], false)
    expect(page.text()).toContain('표시할 프로젝트가 없습니다.')
  })

  it('카드에 이름·상태·진행률을 보여준다', () => {
    const { page } = mountPage([taskGroup])
    expect(page.text()).toContain('메일서버 이중화')
    expect(page.text()).toContain('진행중')
    expect(page.text()).toContain('7/10 완료')
  })

  it('카드에 구분(회사/개인) 배지는 안 보인다 — 위 ScopeSwitch 탭이 이미 구분을 나타낸다', () => {
    const { page } = mountPage([taskGroup])
    // "회사"라는 글자 자체는 설명(description)에도 우연히 들어갈 수 있어
    // 배지 전용 slot 속성으로 확인한다.
    const badgeTexts = page.findAll('[data-slot=badge]').map(b => b.text())
    expect(badgeTexts).not.toContain('회사')
    expect(badgeTexts).not.toContain('개인')
  })

  it('완료 포함이 꺼져 있으면(기본) 완료 상태 카드를 숨긴다', () => {
    const { page } = mountPage([taskGroup, doneTaskGroup])
    expect(page.text()).not.toContain('완료된 프로젝트')
  })

  it('완료 포함을 켜면 완료 상태 카드도 보인다', async () => {
    const { page } = mountPage([taskGroup, doneTaskGroup])
    const includeCompleted = page.findAll('input[type=checkbox]')[0]
    await includeCompleted?.setValue(true)

    expect(page.text()).toContain('완료된 프로젝트')
  })

  it('보관됨 포함을 켜면 store.load를 includeArchived:true로 다시 부른다', async () => {
    const { page } = mountPage([taskGroup])
    const store = useTaskGroupsStore()

    const includeArchived = page.findAll('input[type=checkbox]')[1]
    await includeArchived?.setValue(true)

    expect(store.load).toHaveBeenLastCalledWith(
      expect.objectContaining({ includeArchived: true }),
    )
  })

  it('카드를 클릭하면 상세 화면으로 이동한다', async () => {
    const { page } = mountPage([taskGroup])
    await page.find('[data-slot=card]').trigger('click')

    expect(pushMock).toHaveBeenCalledWith({ name: 'task-group-detail', params: { id: 1 } })
  })

  it('수정·삭제 버튼을 눌러도 카드 클릭(상세 이동)은 일어나지 않는다', async () => {
    const { page } = mountPage([taskGroup])
    const editButton = page.findAll('button').find(b => b.text() === '수정')
    await editButton?.trigger('click')

    expect(pushMock).not.toHaveBeenCalled()
    expect(page.text()).toContain('프로젝트 정보 수정')
  })

  it('삭제 확인 시 할일 개수를 포함한 경고 문구를 보여주고, 확인하면 store.remove를 호출한다', async () => {
    const { page } = mountPage([taskGroup])
    const store = useTaskGroupsStore()
    vi.mocked(store.remove).mockResolvedValue(undefined)

    const deleteButton = page.findAll('button').find(b => b.text() === '삭제')
    await deleteButton?.trigger('click')
    await nextTick()

    expect(page.text()).toContain('할일 10개를 포함해')

    const confirmButtons = page.findAll('button').filter(b => b.text() === '삭제')
    await confirmButtons[confirmButtons.length - 1]?.trigger('click')
    await nextTick()
    await nextTick()

    expect(store.remove).toHaveBeenCalledWith(1)
  })
})
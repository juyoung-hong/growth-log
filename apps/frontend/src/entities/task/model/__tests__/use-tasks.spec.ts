import type { TaskRead } from '@/shared/api'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createTask } from '../../api/create-task'
import { listTasks } from '../../api/list-tasks'
import { updateTaskStatus } from '../../api/update-task-status'
import { useTasksStore } from '../use-tasks'

vi.mock('../../api/create-task')
vi.mock('../../api/list-tasks')
vi.mock('../../api/update-task-status')

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

beforeEach(() => {
  setActivePinia(createPinia())
  vi.clearAllMocks()
})

describe('useTasksStore', () => {
  it('load는 default·all 뷰를 동시에 불러 각각 tasks·allTasks에 담는다', async () => {
    const defaultTasks = [task({ id: 1 })]
    const allTasks = [task({ id: 1 }), task({ id: 2, status: '완료' })]
    vi.mocked(listTasks).mockImplementation((_, view) =>
      Promise.resolve(view === 'all' ? allTasks : defaultTasks),
    )

    const store = useTasksStore()
    await store.load(1)

    expect(store.tasks).toEqual(defaultTasks)
    expect(store.allTasks).toEqual(allTasks)
    expect(listTasks).toHaveBeenCalledWith(1, 'default')
    expect(listTasks).toHaveBeenCalledWith(1, 'all')
  })

  it('load가 끝나기 전까지 loading이 true다', async () => {
    vi.mocked(listTasks).mockResolvedValue([])
    const store = useTasksStore()
    const promise = store.load(1)
    expect(store.loading).toBe(true)
    await promise
    expect(store.loading).toBe(false)
  })

  it('create 성공 후 마지막으로 불렀던 taskGroupId로 다시 읽는다', async () => {
    vi.mocked(listTasks).mockResolvedValue([task()])
    const store = useTasksStore()
    await store.load(7)
    vi.mocked(createTask).mockResolvedValue(task())

    await store.create({ name: '새 태스크' })

    expect(createTask).toHaveBeenCalledWith(7, { name: '새 태스크' })
    expect(listTasks).toHaveBeenLastCalledWith(7, 'all')
  })

  it('불러온 적이 없으면 create가 에러를 던진다', async () => {
    const store = useTasksStore()
    await expect(store.create({ name: '새 태스크' })).rejects.toThrow('불러온 할일목록이 없습니다.')
  })

  it('setLocalStatus는 tasks·allTasks 둘 다에서 같은 id의 상태를 바꾼다', async () => {
    vi.mocked(listTasks).mockResolvedValue([task({ id: 1, status: '보류' })])
    const store = useTasksStore()
    await store.load(1)

    store.setLocalStatus(1, '완료')

    expect(store.tasks[0]?.status).toBe('완료')
    expect(store.allTasks[0]?.status).toBe('완료')
  })

  it('completeTask는 상태를 완료로 바꾸고 목록을 다시 읽는다', async () => {
    vi.mocked(listTasks).mockResolvedValue([task()])
    const store = useTasksStore()
    await store.load(1)
    vi.mocked(updateTaskStatus).mockResolvedValue(task({ status: '완료' }))

    await store.completeTask(1)

    expect(updateTaskStatus).toHaveBeenCalledWith(1, '완료')
    expect(listTasks).toHaveBeenCalledTimes(4) // load(초기 2회) + completeTask의 reload(2회)
  })
})
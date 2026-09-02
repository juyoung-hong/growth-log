import type { TaskGroupRead } from '@/shared/api'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createTaskGroup } from '../../api/create-task-group'
import { deleteTaskGroup } from '../../api/delete-task-group'
import { listTaskGroups } from '../../api/list-task-groups'
import { updateTaskGroup } from '../../api/update-task-group'
import { useTaskGroupsStore } from '../use-task-groups'

vi.mock('../../api/create-task-group')
vi.mock('../../api/delete-task-group')
vi.mock('../../api/list-task-groups')
vi.mock('../../api/update-task-group')

const taskGroup: TaskGroupRead = {
  id: 1,
  category: '회사',
  name: '메일서버 이중화',
  description: null,
  status: '진행중',
  is_archived: false,
  created_at: '2026-08-01T00:00:00Z',
  progress: { total_tasks: 10, done_tasks: 7, percent: 70 },
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.clearAllMocks()
  vi.mocked(listTaskGroups).mockResolvedValue([taskGroup])
})

describe('useTaskGroupsStore', () => {
  it('load가 성공하면 taskGroups를 채운다', async () => {
    const store = useTaskGroupsStore()
    await store.load({ category: '회사' })
    expect(store.taskGroups).toEqual([taskGroup])
    expect(listTaskGroups).toHaveBeenCalledWith({ category: '회사' })
  })

  it('load가 끝나기 전까지 loading이 true다', async () => {
    const store = useTaskGroupsStore()
    const promise = store.load()
    expect(store.loading).toBe(true)
    await promise
    expect(store.loading).toBe(false)
  })

  it('create 성공 후 마지막으로 불렀던 필터로 다시 읽는다', async () => {
    const store = useTaskGroupsStore()
    await store.load({ category: '개인' })
    vi.mocked(createTaskGroup).mockResolvedValue(taskGroup)

    await store.create({ category: '회사', name: '새 프로젝트', status: '진행중' })

    expect(createTaskGroup).toHaveBeenCalledWith({ category: '회사', name: '새 프로젝트', status: '진행중' })
    expect(listTaskGroups).toHaveBeenLastCalledWith({ category: '개인' })
  })

  it('update 성공 후에도 같은 방식으로 다시 읽는다', async () => {
    const store = useTaskGroupsStore()
    await store.load()
    vi.mocked(updateTaskGroup).mockResolvedValue({ ...taskGroup, name: '수정됨' })

    await store.update(1, { name: '수정됨' })

    expect(updateTaskGroup).toHaveBeenCalledWith(1, { name: '수정됨' })
    expect(listTaskGroups).toHaveBeenCalledTimes(2)
  })

  it('remove 성공 후 목록에서 사라진다', async () => {
    const store = useTaskGroupsStore()
    await store.load()
    vi.mocked(deleteTaskGroup).mockResolvedValue(undefined)
    vi.mocked(listTaskGroups).mockResolvedValue([])

    await store.remove(1)

    expect(store.taskGroups).toEqual([])
  })

  it('remove가 실패하면 에러를 그대로 던진다 — TaskGroup 삭제는 항상 성공을 가정하지 않는다', async () => {
    const store = useTaskGroupsStore()
    await store.load()
    vi.mocked(deleteTaskGroup).mockRejectedValue(new Error('network down'))

    await expect(store.remove(1)).rejects.toThrow('network down')
    // 실패했으니 목록은 그대로 남아 있어야 한다(다시 읽지 않는다).
    expect(store.taskGroups).toEqual([taskGroup])
  })
})
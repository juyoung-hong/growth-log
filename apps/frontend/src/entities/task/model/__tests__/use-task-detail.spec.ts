import type { TaskActivityLogRead, TaskCommentRead, TaskRead } from '@/shared/api'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createTaskComment } from '../../api/create-task-comment'
import { deleteTaskComment } from '../../api/delete-task-comment'
import { getTask } from '../../api/get-task'
import { listTaskActivityLog } from '../../api/list-task-activity-log'
import { listTaskComments } from '../../api/list-task-comments'
import { updateTaskComment } from '../../api/update-task-comment'
import { updateTaskSchedule } from '../../api/update-task-schedule'
import { updateTaskStatus } from '../../api/update-task-status'
import { useTaskDetailStore } from '../use-task-detail'

vi.mock('../../api/create-task-comment')
vi.mock('../../api/delete-task-comment')
vi.mock('../../api/get-task')
vi.mock('../../api/list-task-activity-log')
vi.mock('../../api/list-task-comments')
vi.mock('../../api/update-task-comment')
vi.mock('../../api/update-task-schedule')
vi.mock('../../api/update-task-status')

function task(overrides: Partial<TaskRead> = {}): TaskRead {
  return {
    id: 1, task_group_id: 1, name: '이중화 아키텍처 설계', status: '진행중',
    estimated_days: 4, start_date: '2026-08-18', due_date: '2026-08-21',
    completed_at: null, created_at: '2026-08-16T00:00:00Z', ...overrides,
  }
}

const log: TaskActivityLogRead = {
  id: 1, event_type: '등록', event_at: '2026-08-16T00:00:00Z',
  old_value: null, new_value: null, reason: null,
}

const comment: TaskCommentRead = {
  id: 1, task_id: 1, content: 'TTL 300으로 SPF 값 재확인 필요',
  created_at: '2026-08-16T00:00:00Z', updated_at: '2026-08-16T00:00:00Z',
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.clearAllMocks()
  vi.mocked(getTask).mockResolvedValue(task())
  vi.mocked(listTaskActivityLog).mockResolvedValue([log])
  vi.mocked(listTaskComments).mockResolvedValue([comment])
})

describe('useTaskDetailStore', () => {
  it('load는 태스크·활동이력·댓글을 한 번에 불러 채운다', async () => {
    const store = useTaskDetailStore()
    await store.load(1)

    expect(store.task).toEqual(task())
    expect(store.activityLog).toEqual([log])
    expect(store.comments).toEqual([comment])
  })

  it('changeStatus 성공 후 셋 다 다시 읽는다', async () => {
    const store = useTaskDetailStore()
    await store.load(1)
    vi.mocked(updateTaskStatus).mockResolvedValue(task({ status: '완료' }))

    await store.changeStatus('완료')

    expect(updateTaskStatus).toHaveBeenCalledWith(1, '완료')
    expect(getTask).toHaveBeenCalledTimes(2)
    expect(listTaskActivityLog).toHaveBeenCalledTimes(2)
  })

  it('changeSchedule 성공 후 다시 읽는다', async () => {
    const store = useTaskDetailStore()
    await store.load(1)
    vi.mocked(updateTaskSchedule).mockResolvedValue(task({ due_date: '2026-08-25' }))

    await store.changeSchedule({ start_date: '2026-08-18', due_date: '2026-08-25', reason: '순연' })

    expect(updateTaskSchedule).toHaveBeenCalledWith(1, { start_date: '2026-08-18', due_date: '2026-08-25', reason: '순연' })
  })

  it('addComment는 현재 taskId로 등록한 뒤 다시 읽는다', async () => {
    const store = useTaskDetailStore()
    await store.load(1)
    vi.mocked(createTaskComment).mockResolvedValue(comment)

    await store.addComment('새 댓글')

    expect(createTaskComment).toHaveBeenCalledWith(1, { content: '새 댓글' })
    expect(listTaskComments).toHaveBeenCalledTimes(2)
  })

  it('editComment·removeComment는 댓글 id로만 호출하고 다시 읽는다', async () => {
    const store = useTaskDetailStore()
    await store.load(1)
    vi.mocked(updateTaskComment).mockResolvedValue(comment)
    vi.mocked(deleteTaskComment).mockResolvedValue(undefined)

    await store.editComment(1, '수정된 내용')
    expect(updateTaskComment).toHaveBeenCalledWith(1, { content: '수정된 내용' })

    await store.removeComment(1)
    expect(deleteTaskComment).toHaveBeenCalledWith(1)
  })

  it('불러온 적이 없으면 changeStatus가 에러를 던진다', async () => {
    const store = useTaskDetailStore()
    await expect(store.changeStatus('완료')).rejects.toThrow('불러온 태스크가 없습니다.')
  })
})
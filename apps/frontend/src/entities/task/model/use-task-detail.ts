import type {
  TaskActivityLogRead,
  TaskCommentRead,
  TaskRead,
  TaskScheduleUpdate,
  TaskStatus,
} from '@/shared/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createTaskComment } from '../api/create-task-comment'
import { deleteTaskComment } from '../api/delete-task-comment'
import { getTask } from '../api/get-task'
import { listTaskActivityLog } from '../api/list-task-activity-log'
import { listTaskComments } from '../api/list-task-comments'
import { updateTaskComment } from '../api/update-task-comment'
import { updateTaskSchedule } from '../api/update-task-schedule'
import { updateTaskStatus } from '../api/update-task-status'

/**
 * 태스크 상세 화면 하나가 이 store를 쓴다. useTasksStore(레벨2의 할일
 * 목록)와는 다른 store다 — 여긴 태스크 "한 건"과 그 부속물(활동이력·댓글)을
 * 같이 들고 있다.
 */
export const useTaskDetailStore = defineStore('task-detail', () => {
  const task = ref<TaskRead | null>(null)
  const activityLog = ref<TaskActivityLogRead[]>([])
  const comments = ref<TaskCommentRead[]>([])
  const loading = ref(false)
  const currentTaskId = ref<number | null>(null)

  async function load(taskId: number) {
    currentTaskId.value = taskId
    loading.value = true
    try {
      const [taskResult, activityLogResult, commentsResult] = await Promise.all([
        getTask(taskId),
        listTaskActivityLog(taskId),
        listTaskComments(taskId),
      ])
      task.value = taskResult
      activityLog.value = activityLogResult
      comments.value = commentsResult
    }
    finally {
      loading.value = false
    }
  }

  async function reload() {
    if (currentTaskId.value == null) return
    await load(currentTaskId.value)
  }

  async function changeStatus(status: TaskStatus) {
    if (currentTaskId.value == null) throw new Error('불러온 태스크가 없습니다.')
    await updateTaskStatus(currentTaskId.value, status)
    await reload()
  }

  async function changeSchedule(input: TaskScheduleUpdate) {
    if (currentTaskId.value == null) throw new Error('불러온 태스크가 없습니다.')
    await updateTaskSchedule(currentTaskId.value, input)
    await reload()
  }

  async function addComment(content: string) {
    if (currentTaskId.value == null) throw new Error('불러온 태스크가 없습니다.')
    await createTaskComment(currentTaskId.value, { content })
    await reload()
  }

  async function editComment(commentId: number, content: string) {
    await updateTaskComment(commentId, { content })
    await reload()
  }

  async function removeComment(commentId: number) {
    await deleteTaskComment(commentId)
    await reload()
  }

  return {
    task,
    activityLog,
    comments,
    loading,
    load,
    reload,
    changeStatus,
    changeSchedule,
    addComment,
    editComment,
    removeComment,
  }
})
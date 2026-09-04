import type {
  PersonRead,
  TaskActivityLogRead,
  TaskCommentRead,
  TaskRead,
  TaskScheduleUpdate,
  TaskStatus,
} from '@/shared/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { addTaskAssignee } from '../api/add-task-assignee'
import { addTaskDependency } from '../api/add-task-dependency'
import { createTaskComment } from '../api/create-task-comment'
import { deleteTaskComment } from '../api/delete-task-comment'
import { getTask } from '../api/get-task'
import { listTaskActivityLog } from '../api/list-task-activity-log'
import { listTaskAssignees } from '../api/list-task-assignees'
import { listTaskComments } from '../api/list-task-comments'
import { listTaskDependencies } from '../api/list-task-dependencies'
import { removeTaskAssignee } from '../api/remove-task-assignee'
import { removeTaskDependency } from '../api/remove-task-dependency'
import { updateTaskComment } from '../api/update-task-comment'
import { updateTaskSchedule } from '../api/update-task-schedule'
import { updateTaskStatus } from '../api/update-task-status'

export const useTaskDetailStore = defineStore('task-detail', () => {
  const task = ref<TaskRead | null>(null)
  const activityLog = ref<TaskActivityLogRead[]>([])
  const comments = ref<TaskCommentRead[]>([])
  const assignees = ref<PersonRead[]>([])
  const dependencies = ref<TaskRead[]>([])
  const loading = ref(false)
  const currentTaskId = ref<number | null>(null)

  async function load(taskId: number) {
    currentTaskId.value = taskId
    loading.value = true
    try {
      const [taskResult, activityLogResult, commentsResult, assigneesResult, dependenciesResult] = await Promise.all([
        getTask(taskId),
        listTaskActivityLog(taskId),
        listTaskComments(taskId),
        listTaskAssignees(taskId),
        listTaskDependencies(taskId),
      ])
      task.value = taskResult
      activityLog.value = activityLogResult
      comments.value = commentsResult
      assignees.value = assigneesResult
      dependencies.value = dependenciesResult
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

  async function addAssignee(personId: number) {
    if (currentTaskId.value == null) throw new Error('불러온 태스크가 없습니다.')
    await addTaskAssignee(currentTaskId.value, personId)
    await reload()
  }

  async function removeAssignee(personId: number) {
    if (currentTaskId.value == null) throw new Error('불러온 태스크가 없습니다.')
    await removeTaskAssignee(currentTaskId.value, personId)
    await reload()
  }

  async function addDependency(dependsOnTaskId: number) {
    if (currentTaskId.value == null) throw new Error('불러온 태스크가 없습니다.')
    await addTaskDependency(currentTaskId.value, dependsOnTaskId)
    await reload()
  }

  async function removeDependency(dependsOnTaskId: number) {
    if (currentTaskId.value == null) throw new Error('불러온 태스크가 없습니다.')
    await removeTaskDependency(currentTaskId.value, dependsOnTaskId)
    await reload()
  }

  return {
    task, activityLog, comments, assignees, dependencies, loading,
    load, reload, changeStatus, changeSchedule,
    addComment, editComment, removeComment,
    addAssignee, removeAssignee, addDependency, removeDependency,
  }
})
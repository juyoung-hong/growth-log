import type { TaskGroupCreate, TaskGroupRead, TaskGroupUpdate } from '@/shared/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createTaskGroup } from '../api/create-task-group'
import { deleteTaskGroup } from '../api/delete-task-group'
import type { ListTaskGroupsParams } from '../api/list-task-groups'
import { listTaskGroups } from '../api/list-task-groups'
import { updateTaskGroup } from '../api/update-task-group'

/**
 * entities/person과 같은 "쓰면 다시 읽는다" 패턴. status는 이 필터에
 * 없다 — 백엔드 status 필터는 정확히 하나의 상태만 고를 수 있어
 * "완료만 빼고 전부"를 표현할 방법이 없다. 그래서 완료 포함 여부는
 * store가 아니라 pages/task-groups가 store.taskGroups를 그대로 받아
 * 클라이언트에서 걸러낸다.
 */
export const useTaskGroupsStore = defineStore('task-groups', () => {
  const taskGroups = ref<TaskGroupRead[]>([])
  const loading = ref(false)
  const currentParams = ref<ListTaskGroupsParams>({})

  async function load(params: ListTaskGroupsParams = {}) {
    currentParams.value = params
    loading.value = true
    try {
      taskGroups.value = await listTaskGroups(params)
    }
    finally {
      loading.value = false
    }
  }

  async function create(input: TaskGroupCreate) {
    await createTaskGroup(input)
    await load(currentParams.value)
  }

  async function update(id: number, input: TaskGroupUpdate) {
    await updateTaskGroup(id, input)
    await load(currentParams.value)
  }

  async function remove(id: number) {
    await deleteTaskGroup(id)
    await load(currentParams.value)
  }

  return { taskGroups, loading, load, create, update, remove }
})
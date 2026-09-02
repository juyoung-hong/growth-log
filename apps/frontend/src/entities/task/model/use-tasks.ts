import type { TaskCreate, TaskRead, TaskStatus } from '@/shared/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createTask } from '../api/create-task'
import { listTasks } from '../api/list-tasks'
import { updateTaskStatus } from '../api/update-task-status'

/**
 * TaskGroup 상세 화면 하나가 이 store를 쓴다 — TaskGroup 목록 store와
 * 달리 "지금 보고 있는 그룹"이 항상 하나뿐이라 필터 조합(currentParams)
 * 대신 taskGroupId 하나만 든다.
 *
 * 기본 필터(view=default)와 전체(view=all)를 항상 같이 불러와 둔다.
 * "전체보기" 토글이 재요청 없이 즉시 배열만 바꿔 보여줄 수 있고, 숨겨진
 * 건수(완료 몇 건·오래된 보류 몇 건)도 두 배열의 차집합으로 바로 계산할
 * 수 있다 — 30일 기준 같은 필터 로직을 프론트에 다시 구현하지 않아도 된다.
 */
export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref<TaskRead[]>([])
  const allTasks = ref<TaskRead[]>([])
  const loading = ref(false)
  const currentTaskGroupId = ref<number | null>(null)

  async function load(taskGroupId: number) {
    currentTaskGroupId.value = taskGroupId
    loading.value = true
    try {
      const [defaultResult, allResult] = await Promise.all([
        listTasks(taskGroupId, 'default'),
        listTasks(taskGroupId, 'all'),
      ])
      tasks.value = defaultResult
      allTasks.value = allResult
    }
    finally {
      loading.value = false
    }
  }

  async function reload() {
    if (currentTaskGroupId.value == null) return
    await load(currentTaskGroupId.value)
  }

  async function create(input: TaskCreate) {
    if (currentTaskGroupId.value == null) throw new Error('불러온 할일목록이 없습니다.')
    await createTask(currentTaskGroupId.value, input)
    await reload()
  }

  /**
   * 체크박스가 API 응답을 기다리지 않고 먼저 화면에 반영하는 낙관적
   * 업데이트용. 실패하면 호출한 쪽이 이전 상태값으로 다시 불러 되돌린다.
   * tasks·allTasks 둘 다에 반영한다 — "전체보기" 여부와 무관하게 지금
   * 보이는 목록에 바로 체크 표시가 나타나야 한다.
   */
  function setLocalStatus(taskId: number, status: TaskStatus) {
    for (const list of [tasks.value, allTasks.value]) {
      const task = list.find(t => t.id === taskId)
      if (task) task.status = status
    }
  }

  async function completeTask(taskId: number) {
    await updateTaskStatus(taskId, '완료')
    await reload()
  }

  return { tasks, allTasks, loading, load, reload, create, setLocalStatus, completeTask }
})
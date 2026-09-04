<script setup lang="ts">
import type { TaskRead } from '@/shared/api'
import { computed, ref, watch } from 'vue'
import { listTasks, useTaskDetailStore } from '@/entities/task'
import { ApiError } from '@/shared/api'
import { TASK_STATUS_BADGE_COLOR } from '@/shared/lib/task-status'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'

const store = useTaskDetailStore()

const pickerOpen = ref(false)
const query = ref('')
const error = ref('')
const pending = ref(false)

// 선행 후보는 같은 TaskGroup 안에서만 고를 수 있다 — 다른 그룹의
// 태스크를 보내면 서버가 422를 낸다(DependencyTaskGroupMismatchError).
// view=all로 완료·오래된 보류까지 다 후보에 넣는다 — 이미 끝난 작업도
// "그때는 이게 먼저였다"는 기록으로 선행 지정할 수 있어야 한다.
const groupTasks = ref<TaskRead[]>([])

watch(() => store.task?.task_group_id, async (groupId) => {
  if (groupId == null) return
  groupTasks.value = await listTasks(groupId, 'all')
}, { immediate: true })

/**
 * 이름으로 검색하고(TaskAssigneeManage와 같은 이유 — 태스크가 많아지면
 * 스크롤만으로 찾기 어렵다), 이미 완료된 태스크는 뒤로 미룬다 — 지금
 * 진행 중이거나 보류인 태스크가 선행으로 지정할 가능성이 더 높다.
 * status === '완료' 여부만 비교해 정렬하므로 그 안에서는 원래 순서
 * (listTasks가 내려준 순서)가 그대로 유지된다(Array#sort는 안정 정렬).
 */
const candidates = computed(() => {
  if (!store.task) return []
  const dependencyIds = new Set(store.dependencies.map(t => t.id))
  const q = query.value.trim()
  return groupTasks.value
    .filter(t => t.id !== store.task!.id && !dependencyIds.has(t.id))
    .filter(t => !q || t.name.includes(q))
    .sort((a, b) => Number(a.status === '완료') - Number(b.status === '완료'))
})

async function add(taskId: number) {
  pending.value = true
  error.value = ''
  try {
    await store.addDependency(taskId)
    query.value = ''
  }
  catch (e) {
    error.value = e instanceof ApiError ? e.detail : '선행 태스크를 추가하지 못했습니다.'
  }
  finally {
    pending.value = false
  }
}

async function remove(taskId: number) {
  pending.value = true
  error.value = ''
  try {
    await store.removeDependency(taskId)
  }
  catch (e) {
    error.value = e instanceof ApiError ? e.detail : '선행 태스크를 제거하지 못했습니다.'
  }
  finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <h2 class="text-17 font-bold">
      선행 태스크
    </h2>

    <p v-if="store.dependencies.length === 0 && !pickerOpen" class="text-14 text-grey-700">
      선행 태스크가 없습니다.
    </p>

    <ul v-else class="flex flex-col gap-1.5">
      <li
        v-for="dep in store.dependencies"
        :key="dep.id"
        class="bg-grey-100 text-14 text-grey-900 flex items-center gap-2 rounded-[10px] px-3 py-2"
      >
        <span class="flex-1">{{ dep.name }}</span>
        <!-- 완료 여부는 백엔드가 확인하지 않는다(경고조차 없음) — 여기선
             배지+⚠로만 보여준다. 이 태스크(선행 태스크로 지정된 쪽)의 완료
             처리를 실제로 막는 건 그 태스크 자신의 TaskStatusToggle이다. -->
        <Badge :color="TASK_STATUS_BADGE_COLOR[dep.status]" size="small">
          {{ dep.status }}
        </Badge>
        <span v-if="dep.status !== '완료'" aria-hidden="true">⚠</span>
        <button
          type="button"
          class="text-grey-500 hover:text-grey-900"
          :disabled="pending"
          :aria-label="`${dep.name} 선행 태스크에서 제거`"
          @click="remove(dep.id)"
        >
          ×
        </button>
      </li>
    </ul>

    <div v-if="pickerOpen" class="flex flex-col gap-2">
      <Input v-model="query" variant="box" placeholder="이름으로 검색" />
      <ul v-if="candidates.length > 0" class="border-grey-200 flex max-h-40 flex-col overflow-y-auto rounded-[10px] border">
        <li v-for="task in candidates" :key="task.id">
          <button
            type="button"
            class="hover:bg-grey-100 text-14 flex w-full items-center gap-2 px-3 py-2 text-left disabled:opacity-50"
            :disabled="pending"
            @click="add(task.id)"
          >
            <span class="flex-1">{{ task.name }}</span>
            <Badge :color="TASK_STATUS_BADGE_COLOR[task.status]" size="small">
              {{ task.status }}
            </Badge>
          </button>
        </li>
      </ul>
      <p v-else class="text-14 text-grey-700">
        지정할 수 있는 태스크가 없습니다.
      </p>
    </div>

    <Button size="small" variant="weak" color="light" class="self-start" @click="pickerOpen = !pickerOpen; query = ''">
      {{ pickerOpen ? '닫기' : '+ 선행 태스크' }}
    </Button>

    <p v-if="error" class="text-13 text-destructive">
      {{ error }}
    </p>
  </div>
</template>
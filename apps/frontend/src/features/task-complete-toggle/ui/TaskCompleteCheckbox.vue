<script setup lang="ts">
import type { TaskRead } from '@/shared/api'
import { ref } from 'vue'
import { useTasksStore } from '@/entities/task'
import { ApiError } from '@/shared/api'

const props = defineProps<{ task: TaskRead }>()

const store = useTasksStore()
const pending = ref(false)
const error = ref('')

/**
 * 체크박스는 완료로 "표시"만 한다 — 이미 완료된 태스크를 체크 해제해
 * 되돌리는 동작은 이번 단계 범위 밖이다(상태를 자유롭게 오가는 건 레벨3
 * 상세 화면의 몫, 로드맵 5단계). 그래서 완료 상태면 항상 disabled다.
 *
 * API 응답을 기다리지 않고 먼저 화면에 반영한다(낙관적 업데이트) —
 * store.setLocalStatus로 체크 표시가 즉시 바뀌고, 실패하면 이전 상태로
 * 되돌린다. 두 경우 다 store를 거친다 — 컴포넌트가 props.task를 직접
 * 고치지 않는다(부모가 넘긴 객체는 entities/task store가 들고 있는
 * 배열의 항목 그 자체이므로, store를 거치지 않고 직접 고쳐도 화면엔
 * 똑같이 반영되지만 상태 변경 경로를 store 하나로 모아 두는 편이
 * 이 코드베이스의 다른 store들과 일관적이다).
 */
async function complete() {
  if (props.task.status === '완료' || pending.value) return

  const previousStatus = props.task.status
  store.setLocalStatus(props.task.id, '완료')
  pending.value = true
  error.value = ''
  try {
    await store.completeTask(props.task.id)
  }
  catch (e) {
    store.setLocalStatus(props.task.id, previousStatus)
    error.value = e instanceof ApiError ? e.detail : '처리하지 못했습니다.'
  }
  finally {
    pending.value = false
  }
}
</script>

<template>
  <span class="flex items-center gap-1.5">
    <input
      type="checkbox"
      class="accent-primary size-4"
      :checked="task.status === '완료'"
      :disabled="task.status === '완료' || pending"
      :aria-label="`${task.name} 완료 처리`"
      @change="complete"
    >
    <span v-if="error" class="text-13 text-destructive">{{ error }}</span>
  </span>
</template>
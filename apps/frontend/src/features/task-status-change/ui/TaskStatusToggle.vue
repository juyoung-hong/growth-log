<script setup lang="ts">
import type { TaskRead, TaskStatus } from '@/shared/api'
import { computed, ref } from 'vue'
import { useTaskDetailStore } from '@/entities/task'
import { ApiError } from '@/shared/api'
import { TASK_STATUS_BADGE_COLOR, TASK_STATUSES } from '@/shared/lib/task-status'
import { ToggleGroup, ToggleGroupItem } from '@/shared/ui/toggle-group'

const props = defineProps<{ task: TaskRead }>()

const store = useTaskDetailStore()
const pending = ref(false)
const error = ref('')

/**
 * 백엔드는 이 검증을 하지 않는다(change_status가 dependency를 조회조차
 * 하지 않는다) — 선행이 다 끝나기 전엔 완료할 수 없게 한다는 프론트
 * 설계 결정이다(#37 이후 변경). store.dependencies는 useTaskDetailStore가
 * load() 때 이미 같이 불러와 둔 값이라 별도 조회가 필요 없다.
 */
const incompleteDependencies = computed(() => store.dependencies.filter(dep => dep.status !== '완료'))

async function change(status: unknown) {
  const next = status as TaskStatus
  if (next === props.task.status || pending.value) return
  if (next === '완료' && incompleteDependencies.value.length > 0) return

  pending.value = true
  error.value = ''
  try {
    await store.changeStatus(next)
  }
  catch (e) {
    error.value = e instanceof ApiError ? e.detail : '처리하지 못했습니다.'
  }
  finally {
    pending.value = false
  }
}
</script>

<template>
  <div>
    <ToggleGroup :model-value="task.status" stretch @update:model-value="change">
      <ToggleGroupItem
        v-for="status in TASK_STATUSES"
        :key="status"
        :value="status"
        :color="TASK_STATUS_BADGE_COLOR[status]"
        :disabled="pending || (status === '완료' && incompleteDependencies.length > 0)"
      >
        {{ status }}
      </ToggleGroupItem>
    </ToggleGroup>
    <p v-if="task.status !== '완료' && incompleteDependencies.length > 0" class="text-13 text-yellow-800 mt-1.5">
      선행 태스크가 모두 끝나야 완료할 수 있습니다: {{ incompleteDependencies.map(dep => `${dep.name} (${dep.status})`).join(', ') }}
    </p>
    <p v-if="error" class="text-13 text-destructive mt-1.5">
      {{ error }}
    </p>
  </div>
</template>
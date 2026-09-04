<script setup lang="ts">
import type { TaskRead, TaskStatus } from '@/shared/api'
import { ref } from 'vue'
import { useTaskDetailStore } from '@/entities/task'
import { ApiError } from '@/shared/api'
import { TASK_STATUS_BADGE_COLOR, TASK_STATUSES } from '@/shared/lib/task-status'
import { ToggleGroup, ToggleGroupItem } from '@/shared/ui/toggle-group'

const props = defineProps<{ task: TaskRead }>()

const store = useTaskDetailStore()
const pending = ref(false)
const error = ref('')

async function change(status: unknown) {
  const next = status as TaskStatus
  if (next === props.task.status || pending.value) return

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
        :disabled="pending"
      >
        {{ status }}
      </ToggleGroupItem>
    </ToggleGroup>
    <p v-if="error" class="text-13 text-destructive mt-1.5">
      {{ error }}
    </p>
  </div>
</template>
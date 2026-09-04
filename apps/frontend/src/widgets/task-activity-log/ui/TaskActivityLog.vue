<script setup lang="ts">
import { useTaskDetailStore } from '@/entities/task'
import { formatDateTime } from '@/shared/lib/format'
import { formatActivityEvent } from '@/shared/lib/task-activity-log'

const store = useTaskDetailStore()
</script>

<template>
  <div class="flex flex-col gap-2">
    <h2 class="text-17 font-bold">
      활동 이력
    </h2>
    <p v-if="store.activityLog.length === 0" class="text-14 text-grey-700">
      아직 기록이 없습니다.
    </p>
    <ul v-else class="flex flex-col gap-1.5">
      <li v-for="log in store.activityLog" :key="log.id" class="text-14 text-grey-700">
        <span class="text-13 text-grey-500 tabular-nums">{{ formatDateTime(log.event_at) }}</span>
        {{ formatActivityEvent(log) }}
      </li>
    </ul>
  </div>
</template>
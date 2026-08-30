<script setup lang="ts">
import type { StorageQuota } from '@/shared/api'
import { formatBytes } from '@/shared/lib/format'
import { Progress } from '@/shared/ui/progress'

defineProps<{
  label: string
  quota: StorageQuota
  /** 임계치를 넘긴 항목이면 true. 숫자를 빨갛게 보여준다. */
  warning?: boolean
}>()
</script>

<template>
  <div class="flex w-36 items-center gap-2">
    <span class="text-13 text-grey-700 shrink-0">{{ label }}</span>
    <Progress
      :model-value="quota.percent"
      size="normal"
      :color="warning ? 'red' : 'blue'"
    />
    <span
      class="text-13 shrink-0 tabular-nums"
      :class="warning ? 'text-destructive font-semibold' : 'text-grey-700'"
      :title="`${formatBytes(quota.used_bytes)} / ${formatBytes(quota.limit_bytes)}`"
    >
      {{ quota.percent }}%
    </span>
  </div>
</template>
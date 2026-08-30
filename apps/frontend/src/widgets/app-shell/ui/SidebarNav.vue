<script setup lang="ts">
import { HardDrive, ListTodo, Users } from '@lucide/vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()

const ITEMS = [
  { to: '/task-groups', label: '할일관리', icon: ListTodo },
  { to: '/persons', label: '인물관리', icon: Users },
  { to: '/storage', label: '저장공간', icon: HardDrive },
] as const

/**
 * 하위 경로에 있어도 상위 메뉴가 켜져 있어야 한다.
 * 예: /task-groups/3/tasks/7 에서도 '할일관리'가 선택된 상태로 보인다.
 */
function isActive(to: string): boolean {
  return route.path === to || route.path.startsWith(`${to}/`)
}
</script>

<template>
  <nav class="border-border bg-background flex w-52 shrink-0 flex-col gap-1 border-r px-3 pt-5 pb-3">
    <RouterLink
      v-for="item in ITEMS"
      :key="item.to"
      :to="item.to"
      class="text-15 flex items-center gap-2.5 rounded-[10px] px-3 py-2.5 font-medium transition-colors"
      :class="isActive(item.to)
        ? 'bg-accent text-accent-foreground font-semibold'
        : 'text-grey-700 hover:bg-secondary'"
    >
      <component :is="item.icon" class="size-4" />
      {{ item.label }}
    </RouterLink>
  </nav>
</template>
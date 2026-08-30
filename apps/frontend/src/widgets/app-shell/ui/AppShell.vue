<script setup lang="ts">
import { TriangleAlert } from '@lucide/vue'
import { computed } from 'vue'
import { useStorageUsageStore } from '@/entities/storage'
import SidebarNav from './SidebarNav.vue'
import TopBar from './TopBar.vue'

// TopBar가 이미 storage.load()를 호출한다 — 같은 Pinia store 인스턴스라
// 여기서는 읽기만 하면 된다. 두 컴포넌트가 각자 useStorageUsageStore()를
// 부르는 건 중복이 아니라 Pinia의 정상적인 사용법이다.
const storage = useStorageUsageStore()

const warnings = computed(() => storage.usage?.warnings ?? [])

const WARNING_LABELS: Record<string, string> = {
  db: '데이터베이스',
  object_storage: '파일 저장소',
}

const warningText = computed(() =>
  warnings.value.map(key => WARNING_LABELS[key] ?? key).join(' · '),
)
</script>

<template>
  <div class="bg-background text-foreground flex min-h-screen flex-col">
    <TopBar />

    <div v-if="warningText" class="bg-warning-bg text-warning-fg text-15 flex items-center gap-2 px-6 py-2.5">
      <TriangleAlert class="size-4 shrink-0" />
      <span>{{ warningText }} 사용량이 임계치를 넘었습니다. 저장공간을 정리해 주세요.</span>
    </div>

    <div class="flex min-w-0 flex-1">
      <SidebarNav />

      <main class="min-w-0 flex-1 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

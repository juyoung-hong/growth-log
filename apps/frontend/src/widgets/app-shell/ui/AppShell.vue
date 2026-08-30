<script setup lang="ts">
import { TriangleAlert } from '@lucide/vue'
import { computed, onMounted } from 'vue'
import { useStorageUsageStore } from '@/entities/storage'
import SidebarNav from './SidebarNav.vue'
import StorageGauge from './StorageGauge.vue'

const storage = useStorageUsageStore()

onMounted(() => {
  storage.load()
})

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
  <div class="bg-background text-foreground flex min-h-screen">
    <SidebarNav />

    <div class="flex min-w-0 flex-1 flex-col">
      <header class="border-border flex h-14 shrink-0 items-center justify-between gap-4 border-b px-6">
        <span class="text-17 font-bold">growth-log</span>

        <!--
          사용량은 상시 노출한다. Always Free 한도를 넘기면 과금되거나
          인스턴스가 회수되므로, 별도 화면에 들어가야만 보이면 늦는다.
        -->
        <div v-if="storage.usage" class="flex items-center gap-5">
          <StorageGauge label="DB" :quota="storage.usage.db" :warning="warnings.includes('db')" />
          <StorageGauge label="파일" :quota="storage.usage.object_storage" :warning="warnings.includes('object_storage')" />
        </div>
      </header>

      <div v-if="warningText" class="bg-warning-bg text-warning-fg text-15 flex items-center gap-2 px-6 py-2.5">
        <TriangleAlert class="size-4 shrink-0" />
        <span>{{ warningText }} 사용량이 임계치를 넘었습니다. 저장공간을 정리해 주세요.</span>
      </div>

      <main class="min-w-0 flex-1 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>
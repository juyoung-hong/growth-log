<script setup lang="ts">
import { Sprout } from '@lucide/vue'
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useStorageUsageStore } from '@/entities/storage'
import { Button } from '@/shared/ui/button'
import StorageGauge from './StorageGauge.vue'

/**
 * 전역 바 — 로고(홈 링크) · 저장공간 게이지 · 로그인(아직 미구현).
 * 사이드바(SidebarNav)의 "할일관리·인물관리·저장공간"은 이 화면들
 * 사이의 이동이고, 이 바는 그보다 위에 있는 앱 전체 단위의 자리다.
 *
 * 로그인은 아직 인증을 붙이지 않아서 disabled로 존재만 표시한다.
 * 버튼을 아예 숨기면 "여기 로그인이 생길 것"이라는 정보 자체가
 * 사라지고, 눌리는 것처럼 보이는데 아무 일도 안 일어나는 것보다는
 * disabled로 의도를 분명히 하는 쪽이 낫다고 판단했다.
 */
const storage = useStorageUsageStore()

onMounted(() => {
  storage.load()
})
</script>

<template>
  <header class="border-border bg-background flex h-14 shrink-0 items-center justify-between gap-4 border-b px-6">
    <RouterLink to="/" class="text-17 text-foreground flex shrink-0 items-center gap-2 font-bold">
      <Sprout class="text-primary size-5" />
      성장일기
    </RouterLink>

    <!--
      로고와 [게이지 + 로그인] 두 그룹만 justify-between으로 양 끝에 둔다.
      게이지를 로고·로그인과 나란히 세 번째 축으로 두면 space-between이
      가운데로 밀어버린다 — 로그인 바로 왼쪽에 붙이려면 한 그룹으로 묶어야 한다.
    -->
    <div class="flex items-center gap-5">
      <!--
        사용량은 상시 노출한다. Always Free 한도를 넘기면 과금되거나
        인스턴스가 회수되므로, 별도 화면에 들어가야만 보이면 늦는다.
      -->
      <div v-if="storage.usage" class="flex items-center gap-5">
        <StorageGauge label="DB" :quota="storage.usage.db" :warning="storage.usage.warnings.includes('db')" />
        <StorageGauge label="파일" :quota="storage.usage.object_storage" :warning="storage.usage.warnings.includes('object_storage')" />
      </div>

      <Button size="small" variant="weak" color="light" disabled title="준비 중입니다">
        로그인
      </Button>
    </div>
  </header>
</template>

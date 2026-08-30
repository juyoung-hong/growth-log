<script setup lang="ts">
import type { ScopeParam } from '@/shared/lib/scope'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { parseScopeParam, SCOPE_LABELS, SCOPE_PARAMS } from '@/shared/lib/scope'
import { Tabs, TabsList, TabsTrigger } from '@/shared/ui/tabs'

const route = useRoute()
const router = useRouter()

const current = computed(() => parseScopeParam(route.query.scope))

/**
 * 개인/회사는 별도 라우트가 아니라 같은 화면의 쿼리 파라미터다.
 * push가 아니라 replace를 쓰는 이유 — 탭을 여러 번 오간 뒤 뒤로가기를
 * 누르면 이전 화면이 아니라 탭 전환 이력이 하나씩 되감기기 때문이다.
 */
function change(value: string | number) {
  router.replace({ query: { ...route.query, scope: value as ScopeParam } })
}
</script>

<template>
  <Tabs :model-value="current" @update:model-value="change">
    <TabsList>
      <TabsTrigger v-for="param in SCOPE_PARAMS" :key="param" :value="param">
        {{ SCOPE_LABELS[param] }}
      </TabsTrigger>
    </TabsList>
  </Tabs>
</template>
<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/shared/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <!--
    자체 배경·구분선을 넣지 않는다. Card.vue의 원칙(내부는 Border/Separator로
    나눈다)과 어긋난다 — 위에 구분이 필요하면 호출부가 <Separator variant="full" />를
    명시적으로 놓는다. shadcn 기본값은 border-t + bg-muted/50을 자동으로
    넣었는데, 그러면 Separator를 쓴 자리와 안 쓴 자리가 뒤섞여 규칙이
    두 갈래로 갈린다.
  -->
  <div
    data-slot="card-footer"
    :class="cn('p-4 group-data-[size=sm]/card:p-3 flex items-center', props.class)"
  >
    <slot />
  </div>
</template>

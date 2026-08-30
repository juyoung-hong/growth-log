<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/shared/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <div
    data-slot="card-title"
    :class="cn('text-16 leading-snug font-medium group-data-[size=sm]/card:text-14 cn-font-heading', props.class)"
  >
    <slot />
  </div>
</template>

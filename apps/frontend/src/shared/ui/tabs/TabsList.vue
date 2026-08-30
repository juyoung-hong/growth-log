<script setup lang="ts">
import type { TabsListProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import type { TabsListVariants } from '.'
import { computed } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { TabsList } from 'reka-ui'
import { cn } from '@/shared/lib/utils'
import { tabsListVariants } from '.'

const props = withDefaults(defineProps<TabsListProps & {
  class?: HTMLAttributes['class']
  size?: TabsListVariants['size']
  /** 4개 넘는 탭을 가로 스크롤로 보여줄지. TDS 지침: 4개 넘으면 켜라. */
  fluid?: boolean
  /** 탭 사이 간격(px). 지정 안 하면 기본 gap(16px)을 쓴다. */
  itemGap?: number
  ariaLabel?: string
}>(), {
  size: 'large',
  fluid: false,
  itemGap: undefined,
  ariaLabel: undefined,
})

const delegatedProps = reactiveOmit(props, 'class', 'size', 'fluid', 'itemGap', 'ariaLabel')

const gapStyle = computed(() =>
  props.itemGap == null ? undefined : { gap: `${props.itemGap}px` },
)
</script>

<template>
  <TabsList
    data-slot="tabs-list"
    :data-size="size"
    :aria-label="ariaLabel"
    v-bind="delegatedProps"
    :style="gapStyle"
    :class="cn(tabsListVariants({ size, fluid }), !itemGap && 'gap-4', props.class)"
  >
    <slot />
  </TabsList>
</template>

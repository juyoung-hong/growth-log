<script setup lang="ts">
import type { RadioGroupItemProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import type { BadgeVariants } from '@/shared/ui/badge'
import { reactiveOmit } from '@vueuse/core'
import { RadioGroupItem, useForwardProps } from 'reka-ui'
import { cn } from '@/shared/lib/utils'
import { TOGGLE_GROUP_ITEM_COLOR } from '.'

const props = defineProps<RadioGroupItemProps & {
  class?: HTMLAttributes['class']
  /** 선택됐을 때 채울 색. Badge와 같은 색 축을 쓴다(index.ts 참고). */
  color: NonNullable<BadgeVariants['color']>
}>()

const delegatedProps = reactiveOmit(props, 'class', 'color')
const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <RadioGroupItem
    data-slot="toggle-group-item"
    :class="cn(
      'inline-flex h-9 items-center justify-center rounded-[8px] px-3 text-14 font-bold whitespace-nowrap transition-colors outline-none',
      'bg-grey-100 text-grey-800 hover:bg-grey-200',
      'focus-visible:ring-3 focus-visible:ring-ring/50',
      'disabled:pointer-events-none disabled:opacity-40',
      'group-data-[stretch=true]/toggle-group:flex-1',
      TOGGLE_GROUP_ITEM_COLOR[color],
      props.class,
    )"
    v-bind="forwardedProps"
  >
    <slot />
  </RadioGroupItem>
</template>

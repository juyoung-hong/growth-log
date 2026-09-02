<script setup lang="ts">
import type { RadioGroupRootEmits, RadioGroupRootProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { RadioGroupRoot, useForwardPropsEmits } from 'reka-ui'
import { cn } from '@/shared/lib/utils'

const props = defineProps<RadioGroupRootProps & {
  class?: HTMLAttributes['class']
  /** 항목마다 폭을 균등하게 나눠 채운다. Tabs의 stretch와 같은 이유. */
  stretch?: boolean
}>()
const emits = defineEmits<RadioGroupRootEmits>()

const delegatedProps = reactiveOmit(props, 'class', 'stretch')
const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <RadioGroupRoot
    data-slot="toggle-group"
    :data-stretch="stretch"
    v-bind="forwarded"
    :class="cn('group/toggle-group flex gap-1.5', props.class)"
  >
    <slot />
  </RadioGroupRoot>
</template>

<script setup lang="ts">
import type { SeparatorProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { Separator } from 'reka-ui'
import { computed } from 'vue'
import { cn } from '@/shared/lib/utils'

/**
 * TDS 인터페이스(variant/height) + Open Color 값.
 * https://tossmini-docs.toss.im/tds-mobile/components/border/
 *
 * 구분선을 세 가지로 쓴다 —
 *   full      : 폭을 꽉 채운 1px 선
 *   padding24 : 좌우 24px을 비운 1px 선 (카드 안 항목 사이)
 *   height16  : 선 없이 16px 여백만 (문단을 갈라놓을 때)
 * Border는 "선"이 아니라 "구분"을 뜻하는 부품이라 여백도 같은 이름 아래 둔다.
 *
 * 테두리 색(--border, grey-200)은 그대로 쓴다. Input의 테두리와 달리
 * 사용자가 조작해야 하는 경계가 아니라 내용을 훑어보기 쉽게 나누는
 * 장식적 구분이라, WCAG 3.0:1 기준을 적용하지 않는다 — 12-table.md에서
 * 테이블 행 구분선에 적용한 것과 같은 판단이다.
 */
const props = withDefaults(
  defineProps<
    SeparatorProps & {
      class?: HTMLAttributes['class']
      variant?: 'full' | 'padding24' | 'height16'
      /** height16 전용. 기본 16px 대신 원하는 높이(px)를 쓰고 싶을 때. */
      height?: number
    }
  >(),
  {
    orientation: 'horizontal',
    decorative: true,
    variant: 'full',
    height: undefined,
  },
)

const delegatedProps = reactiveOmit(props, 'class', 'variant', 'height')

const VARIANTS = {
  'full': 'bg-border',
  'padding24': 'bg-border mx-6 w-[calc(100%-3rem)]',
  'height16': 'bg-transparent data-[orientation=horizontal]:h-4',
} as const

const heightStyle = computed(() =>
  props.variant === 'height16' && props.height != null
    ? { height: `${props.height}px` }
    : undefined,
)
</script>

<template>
  <Separator
    data-slot="separator"
    v-bind="delegatedProps"
    :style="heightStyle"
    :class="
      cn(
        'shrink-0 data-[orientation=horizontal]:h-px data-[orientation=horizontal]:w-full data-[orientation=vertical]:w-px data-[orientation=vertical]:self-stretch',
        VARIANTS[variant],
        props.class,
      )
    "
  />
</template>

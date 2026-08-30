<script setup lang="ts">
import type { ProgressRootProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { ProgressIndicator, ProgressRoot } from 'reka-ui'
import { cn } from '@/shared/lib/utils'

/**
 * TDS 인터페이스(size/color/animate) + Open Color 값.
 * https://tossmini-docs.toss.im/tds-mobile/components/progress-bar/
 *
 * TDS의 progress(0.0~1.0)를 그대로 쓰지 않고 modelValue(0~100)를 쓴다.
 * Reka UI ProgressRoot의 기본 규약이 0~100이고, 백엔드가
 * TaskGroupProgress.percent를 이미 0~100으로 내려주므로 변환 없이
 * 그대로 넘길 수 있다 — 굳이 0.0~1.0으로 한 번 더 바꿀 이유가 없었다.
 *
 * TDS의 color는 아무 CSS 값이나 받는 열린 문자열이지만, 이 프로젝트는
 * 리터럴 hex를 직접 쓰지 않고 팔레트 토큰으로만 색을 고른다는 원칙이
 * 있다(01-colors.md). 그래서 color를 Badge와 같은 13개 hue 이름으로
 * 닫힌 목록으로 만들었다.
 */
const props = withDefaults(
  defineProps<
    ProgressRootProps & {
      class?: HTMLAttributes['class']
      size?: 'light' | 'normal' | 'bold'
      color?:
        | 'blue' | 'red' | 'pink' | 'purple' | 'violet' | 'indigo'
        | 'cyan' | 'teal' | 'green' | 'lime' | 'yellow' | 'orange' | 'grey'
      /** 값이 바뀔 때 부드럽게 움직일지. TDS 기본값(false)을 그대로 따른다 —
       * 목록에 여러 개가 한꺼번에 그려질 때 전부 애니메이션되면 산만하다. */
      animate?: boolean
    }
  >(),
  {
    modelValue: 0,
    size: 'normal',
    color: 'blue',
    animate: false,
  },
)

const delegatedProps = reactiveOmit(props, 'class', 'size', 'color', 'animate')

const HEIGHTS = { light: 'h-0.5', normal: 'h-1', bold: 'h-1.5' } as const

// 괄호 안은 트랙(grey-200)과의 실측 명도 대비비(WCAG 비텍스트 기준 3.0:1).
// blue만 최소 통과 단계(600, 3.00 — 반올림 경계라 여유가 없다)보다
// 한 단계 위인 700을 쓴다. 기본 색이라 다른 색보다 훨씬 자주 보이므로
// 여유를 둔 것이고, 나머지 12색은 3.0을 넘기는 가장 얕은 단계를 쓴다.
const COLORS = {
  blue: 'bg-blue-700', //     3.54 — 기본색, 의도적으로 여유를 둠
  red: 'bg-red-700', //       3.24
  pink: 'bg-pink-600', //     3.15
  purple: 'bg-purple-600', // 3.39
  violet: 'bg-violet-500', // 3.60
  indigo: 'bg-indigo-500', // 3.10
  cyan: 'bg-cyan-800', //     3.67
  teal: 'bg-teal-800', //     3.33
  green: 'bg-green-900', //   3.68
  lime: 'bg-lime-900', //     3.11
  // yellow는 900단계로도 3.0을 못 넘긴다(2.53) — Badge의 green·yellow와
  // 같은 판단으로, 색상 예외를 두지 않고 그대로 쓴다.
  yellow: 'bg-yellow-900', // 2.53 — AA 미달, 원칙 우선
  orange: 'bg-orange-800', // 3.02
  grey: 'bg-grey-700', //     6.90
} as const
</script>

<template>
  <ProgressRoot
    data-slot="progress"
    v-bind="delegatedProps"
    :class="cn('bg-grey-200 relative flex w-full items-center overflow-hidden rounded-full', HEIGHTS[size], props.class)"
  >
    <ProgressIndicator
      data-slot="progress-indicator"
      :class="cn('size-full flex-1', COLORS[color], animate && 'transition-all')"
      :style="`transform: translateX(-${100 - (props.modelValue ?? 0)}%);`"
    />
  </ProgressRoot>
</template>

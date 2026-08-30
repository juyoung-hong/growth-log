<script setup lang="ts">
import type { TabsTriggerProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { TabsTrigger, useForwardProps } from 'reka-ui'
import { cn } from '@/shared/lib/utils'

const props = withDefaults(defineProps<TabsTriggerProps & {
  class?: HTMLAttributes['class']
  /** 새 소식이 있음을 알리는 빨간 점. TDS의 Tab.Item.redBean. */
  redBean?: boolean
}>(), {
  redBean: false,
})

const delegatedProps = reactiveOmit(props, 'class', 'redBean')

const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <TabsTrigger
    data-slot="tabs-trigger"
    :class="cn(
      'relative inline-flex h-full items-center justify-center gap-1.5 whitespace-nowrap px-0.5 font-medium text-grey-700 outline-none transition-colors',
      'hover:text-grey-900 focus-visible:ring-3 focus-visible:ring-ring/50',
      'disabled:pointer-events-none disabled:opacity-40',
      'data-active:font-bold data-active:text-grey-900',
      'group-data-[size=large]/tabs-list:text-17 group-data-[size=small]/tabs-list:text-14',
      // stretch=false(기본)면 자기 글자 폭만큼만 차지한다(shrink-0으로 안
      // 찌그러지게). stretch=true면 항목마다 남는 폭을 균등하게 나눠 갖는다
      // — TabsList가 이미 justify-center를 각 트리거에 주고 있어 늘어난
      // 폭 안에서 글자는 그대로 가운데에 남는다.
      'group-data-[stretch=false]/tabs-list:shrink-0 group-data-[stretch=true]/tabs-list:flex-1',
      // 회색 기준선은 TabsList가 목록 전체 폭에 한 번만 그린다(index.ts).
      // 여기서는 선택된 탭 위에만 파란 강조선을 겹친다 — z-10으로 기준선
      // 위에 그려지게 해서 끊김 없이 하나로 이어진 선처럼 보인다.
      // 글자 폭(inset-x-0)보다 좌우로 4px씩 더 넓게 그린다 — 탭 사이 간격이
      // 16px(gap-4)이라 양쪽에서 4px씩 먹어도 8px이 남아 옆 탭을 침범하지 않는다.
      'after:absolute after:-inset-x-1 after:bottom-0 after:z-10 after:h-0.5 after:rounded-full after:bg-primary after:opacity-0 after:transition-opacity',
      'data-active:after:opacity-100',
      '[&_svg]:pointer-events-none [&_svg]:shrink-0',
      props.class,
    )"
    v-bind="forwardedProps"
  >
    <slot />
    <!-- redBean: 시각 표시(점)와 스크린리더 안내를 함께 준다. TDS는 title
         속성에 "(업데이트 있음)"을 자동으로 붙이는데, title은 호버해야만
         읽히는 보조기술도 있어 더 확실히 전달되는 sr-only 텍스트를 쓴다. -->
    <span v-if="redBean" aria-hidden="true" class="bg-red-600 absolute top-0.5 right-0.5 size-1.5 rounded-full" />
    <span v-if="redBean" class="sr-only">(업데이트 있음)</span>
  </TabsTrigger>
</template>

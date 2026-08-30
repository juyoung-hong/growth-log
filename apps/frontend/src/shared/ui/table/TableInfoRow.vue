<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/shared/lib/utils'

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes['class']
    /** TDS는 필수로 두고 기본값이 없지만, 이 구현은 space-between을
     * 기본값으로 둔다 — "왼쪽 라벨 : 오른쪽 값"이 이 컴포넌트가 쓰이는
     * 가장 흔한 모양이라 매번 지정하지 않아도 되게 했다. */
    align?: 'left' | 'space-between'
    /** 왼쪽 영역이 전체 폭에서 차지할 비율(%). 안 주면 내용 크기만큼만 차지한다. */
    leftRatio?: number
  }>(),
  {
    class: undefined,
    align: 'space-between',
    leftRatio: undefined,
  },
)
</script>

<template>
  <div
    data-slot="table-info-row"
    :class="cn(
      'flex items-center gap-3 py-2 text-15',
      align === 'space-between' ? 'justify-between' : 'justify-start',
      props.class,
    )"
  >
    <div
      class="text-grey-700 shrink-0"
      :style="leftRatio != null ? { flex: `0 0 ${leftRatio}%` } : undefined"
    >
      <slot name="left" />
    </div>
    <div :class="cn('text-grey-900 min-w-0', align === 'space-between' && 'text-right')">
      <slot name="right" />
    </div>
  </div>
</template>

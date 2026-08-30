<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { AlertVariants } from '.'
import { computed, onBeforeUnmount, watch } from 'vue'
import { cn } from '@/shared/lib/utils'
import { alertVariants } from '.'

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes['class']
    variant?: AlertVariants['variant']
    /** true면 TDS Toast처럼 화면에 떠서 일정 시간 뒤 자동으로 사라진다.
     * false(기본)면 지금까지처럼 페이지 안에 계속 머무는 정적 배너다. */
    floating?: boolean
    /** floating일 때의 표시 여부(v-model). 정적 배너는 호출부의 v-if로
     * 조건부 렌더링하면 되므로 안 쓴다. */
    open?: boolean
    position?: 'top' | 'bottom'
    /** 자동으로 닫히기까지 걸리는 시간(ms). 0이면 자동으로 안 닫힌다.
     * floating일 때만 쓴다. TDS 기본값(3000ms)을 그대로 따른다. */
    duration?: number
    /** 지정 안 하면 destructive는 assertive, 나머지는 polite로 스스로
     * 정한다 — 에러는 지금 하던 걸 끊고서라도 즉시 알려야 하고, 나머지는
     * 읽던 흐름을 방해하지 않는 쪽이 낫다. */
    ariaLive?: 'polite' | 'assertive'
  }>(),
  {
    class: undefined,
    variant: 'default',
    floating: false,
    open: true,
    position: 'bottom',
    duration: 3000,
    ariaLive: undefined,
  },
)

const emit = defineEmits<{ 'update:open': [value: boolean] }>()

const resolvedAriaLive = computed(() =>
  props.ariaLive ?? (props.variant === 'destructive' ? 'assertive' : 'polite'),
)
// role="alert"는 aria-live="assertive"를, role="status"는 "polite"를
// 암시한다(ARIA 명세). 명시적 aria-live와 짝이 맞는 role을 같이 쓴다.
const role = computed(() => (resolvedAriaLive.value === 'assertive' ? 'alert' : 'status'))

let timer: ReturnType<typeof setTimeout> | undefined

function scheduleAutoClose() {
  clearTimeout(timer)
  if (!props.floating || !props.open || props.duration <= 0) return
  timer = setTimeout(() => emit('update:open', false), props.duration)
}

watch(() => [props.floating, props.open, props.duration], scheduleAutoClose, { immediate: true })
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
  <Teleport v-if="floating" to="body">
    <Transition
      enter-active-class="transition-all duration-150"
      leave-active-class="transition-all duration-150"
      enter-from-class="opacity-0 translate-y-1"
      leave-to-class="opacity-0 translate-y-1"
    >
      <div
        v-if="open"
        data-slot="alert"
        :role="role"
        :aria-live="resolvedAriaLive"
        aria-atomic="true"
        :class="cn(
          alertVariants({ variant }),
          // 정적 Alert와 달리 뒤에 딤머가 없어 배경과 구분이 잘 안 된다.
          // 이 프로젝트에서 그림자를 쓰는 유일한 자리다 — Card·Dialog는
          // 배경색 차이나 딤머로 구분하지만, 떠 있는 토스트는 그 방법이
          // 없어서 예외를 둔다.
          'shadow-lg fixed inset-x-4 z-50 mx-auto max-w-sm',
          position === 'top' ? 'top-4' : 'bottom-4',
          props.class,
        )"
      >
        <slot />
      </div>
    </Transition>
  </Teleport>

  <div
    v-else
    data-slot="alert"
    role="alert"
    :class="cn(alertVariants({ variant }), props.class)"
  >
    <slot />
  </div>
</template>

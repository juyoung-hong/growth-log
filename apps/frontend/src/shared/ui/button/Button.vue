<script setup lang="ts">
import type { PrimitiveProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import type { ButtonVariants } from '.'
import { LoaderCircle } from '@lucide/vue'
import { Primitive } from 'reka-ui'
import { cn } from '@/shared/lib/utils'
import { buttonVariants } from '.'

interface Props extends PrimitiveProps {
  variant?: ButtonVariants['variant']
  color?: ButtonVariants['color']
  display?: ButtonVariants['display']
  size?: ButtonVariants['size']
  loading?: boolean
  disabled?: boolean
  /** 네이티브 <button>의 type 속성. 폼 안에 있어도 기본은 submit이 아니라
   * button이다 — 의도치 않은 폼 제출을 막기 위해 TDS와 달리 기본값을
   * 명시적으로 둔다. */
  type?: 'button' | 'submit' | 'reset'
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  as: 'button',
  loading: false,
  disabled: false,
  type: 'button',
})
</script>

<template>
  <Primitive
    data-slot="button"
    :data-variant="variant"
    :data-color="color"
    :data-display="display"
    :data-size="size"
    :as="as"
    :as-child="asChild"
    :type="type"
    :disabled="disabled || loading"
    :data-loading="loading ? '' : undefined"
    :class="cn(buttonVariants({ variant, color, display, size }), props.class)"
  >
    <!-- 로딩 중에도 글자를 지우지 않는다. 버튼 너비가 흔들리면
         연타나 오클릭이 생기기 때문이다. -->
    <LoaderCircle v-if="loading" class="animate-spin" />
    <slot />
  </Primitive>
</template>

<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { InputVariants } from '.'
import { useVModel } from '@vueuse/core'
import { XIcon } from '@lucide/vue'
import { computed, useId } from 'vue'
import { cn } from '@/shared/lib/utils'
import { inputVariants } from '.'

const props = withDefaults(
  defineProps<{
    variant: InputVariants['variant']
    /** true면 <textarea>로 렌더링한다(TDS TextArea에 대응). prefix/suffix는
     * 여러 줄에는 의미가 없어 무시된다 — TDS TextArea도 그 셋을 뺀다. */
    multiline?: boolean
    label?: string
    /** appear(기본): label을 자리표시자로만 보여준다.
     * sustain: label을 입력창 위에 항상 띄운다. */
    labelOption?: 'appear' | 'sustain'
    help?: string
    hasError?: boolean
    disabled?: boolean
    prefix?: string
    suffix?: string
    placeholder?: string
    /** 값이 있을 때 지우기 버튼을 보여줄지. TDS의 TextField.Clearable과
     * SearchField의 내장 지우기 버튼을 여기 하나로 흡수했다. */
    clearable?: boolean
    type?: string
    /** TextArea 전용. variant의 기본 min-h-*를 넘어서는 값이 필요할 때. */
    minHeight?: number
    height?: number
    modelValue?: string | number
    defaultValue?: string | number
    class?: HTMLAttributes['class']
  }>(),
  {
    multiline: false,
    label: undefined,
    labelOption: 'appear',
    help: undefined,
    hasError: false,
    disabled: false,
    prefix: undefined,
    suffix: undefined,
    placeholder: undefined,
    clearable: false,
    type: 'text',
    minHeight: undefined,
    height: undefined,
    modelValue: undefined,
    defaultValue: undefined,
    class: undefined,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  'clear': []
}>()

const modelValue = useVModel(props, 'modelValue', emit, {
  passive: true,
  defaultValue: props.defaultValue,
})

const inputId = useId()

const effectivePlaceholder = computed(() =>
  props.labelOption === 'sustain' ? props.placeholder : (props.placeholder ?? props.label),
)

const sizeStyle = computed(() => {
  if (!props.multiline) return undefined
  const style: Record<string, string> = {}
  if (props.minHeight != null) style.minHeight = `${props.minHeight}px`
  if (props.height != null) style.height = `${props.height}px`
  return style
})

function clear() {
  modelValue.value = ''
  emit('clear')
}
</script>

<template>
  <div class="flex w-full flex-col gap-1.5">
    <label
      v-if="label"
      :for="inputId"
      :class="labelOption === 'sustain' ? 'text-14 text-grey-800 font-medium' : 'sr-only'"
    >
      {{ label }}
    </label>

    <div
      data-slot="input"
      :style="sizeStyle"
      :class="cn(inputVariants({ variant, multiline, hasError }), props.class)"
    >
      <span v-if="prefix && !multiline" class="text-grey-700 shrink-0">{{ prefix }}</span>

      <textarea
        v-if="multiline"
        :id="inputId"
        v-model="modelValue"
        :disabled="disabled"
        :placeholder="effectivePlaceholder"
        :aria-invalid="hasError"
        class="min-w-0 flex-1 resize-y bg-transparent text-grey-900 outline-none placeholder:text-grey-700 disabled:cursor-not-allowed"
      />
      <input
        v-else
        :id="inputId"
        v-model="modelValue"
        :type="type"
        :disabled="disabled"
        :placeholder="effectivePlaceholder"
        :aria-invalid="hasError"
        class="min-w-0 flex-1 bg-transparent text-grey-900 outline-none placeholder:text-grey-700 disabled:cursor-not-allowed"
      >

      <span v-if="suffix && !multiline" class="text-grey-700 shrink-0">{{ suffix }}</span>

      <button
        v-if="clearable && modelValue"
        type="button"
        aria-label="입력값 지우기"
        class="text-grey-600 hover:text-grey-700 shrink-0"
        @click="clear"
      >
        <XIcon class="size-4" />
      </button>
      <slot v-else name="right" />
    </div>

    <p
      v-if="help"
      :class="cn('text-14', hasError ? 'text-destructive' : 'text-grey-700')"
    >
      {{ help }}
    </p>
  </div>
</template>

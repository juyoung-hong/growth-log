<script setup lang="ts">
import type { DateValue } from '@internationalized/date'
import type { HTMLAttributes } from 'vue'
import { parseDate } from '@internationalized/date'
import { Calendar as CalendarIcon, XIcon } from '@lucide/vue'
import { PopoverAnchor, PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'
import { computed, ref, useId } from 'vue'
import { cn } from '@/shared/lib/utils'
import { Calendar } from '@/shared/ui/calendar'
import { inputVariants } from '@/shared/ui/input'

/**
 * Input(variant="box")과 같은 자리에 끼워 넣을 수 있도록 label·labelOption·
 * help·hasError를 그대로 흉내 낸다 — 네이티브 <input type="date">를
 * 대체하는 자리(태스크 등록·일정 변경)에서 다른 필드와 똑같이 보이게
 * 하려는 것이다. v-model은 Input과 마찬가지로 'YYYY-MM-DD' 문자열이다
 * (비었으면 '') — 호출하는 쪽 폼 코드를 하나도 안 고쳐도 되게 하려고
 * @internationalized/date의 CalendarDate로의 변환은 이 컴포넌트 안에서만 한다.
 */
const props = withDefaults(defineProps<{
  label?: string
  labelOption?: 'appear' | 'sustain'
  help?: string
  hasError?: boolean
  disabled?: boolean
  placeholder?: string
  /** ISO 날짜 문자열(YYYY-MM-DD) — 빨간색으로 표시할 날짜(공휴일 등).
   * Calendar에 그대로 전달한다. */
  holidays?: string[]
  modelValue?: string
  class?: HTMLAttributes['class']
}>(), {
  label: undefined,
  labelOption: 'appear',
  help: undefined,
  hasError: false,
  disabled: false,
  placeholder: undefined,
  holidays: () => [],
  modelValue: '',
  class: undefined,
})

const emit = defineEmits<{
  'update:modelValue': [string]
}>()

const fieldId = useId()
const open = ref(false)

const calendarValue = computed<DateValue | undefined>(() => props.modelValue ? parseDate(props.modelValue) : undefined)

/**
 * '날짜 선택'까지 최종 fallback을 둔다 — sustain 라벨(일정 변경 다이얼로그처럼
 * placeholder를 따로 안 넘기는 자리)에서 값이 비면 이 문구조차 없이 완전히
 * 빈 문자열이 트리거 버튼에 들어간다. 텍스트 없는 <button>은 줄 높이를
 * 만들 내용이 없어 실제 브라우저에서 세로로 찌그러질 수 있고, 그러면
 * 감싸는 38px 박스 안에서 위아래 여백만 클릭돼 버튼을 못 누르는 것처럼
 * 보인다 — 시작일(값이 항상 있어 늘 텍스트가 있음)은 멀쩡한데 마감일을
 * 비운 채로 열면 안 열리던 문제가 이것이었다.
 */
const effectivePlaceholder = computed(() =>
  (props.labelOption === 'sustain' ? props.placeholder : (props.placeholder ?? props.label)) ?? '날짜 선택',
)

function select(date: DateValue | undefined) {
  emit('update:modelValue', date ? date.toString() : '')
  open.value = false
}

/**
 * PopoverTrigger는 <button>이라, 지우기 버튼도 <button>으로 그 안에
 * 넣으면 버튼 안에 버튼이 들어가는 잘못된 HTML이 된다(Input.vue의
 * clearable과 달리 여기선 바깥 컨테이너가 <input>이 아니라 트리거
 * 자체가 버튼이라서 생기는 차이다). 그래서 박스 스타일은 감싸는 <div>로
 * 옮기고, 트리거는 텍스트 영역만 차지하는 버튼으로 좁혀서 지우기
 * 버튼과 형제로 나란히 둔다.
 *
 * 지우기 버튼은 open 상태를 건드리지 않는 별개 엘리먼트다 — 달력이
 * 열려 있는 채로 지우기를 누르면(트리거를 다시 닫지 않고) open이
 * true로 남는다. 트리거는 클릭할 때마다 열림 상태를 그대로
 * 토글하므로, 그다음 트리거 클릭이 "열기"가 아니라 "닫기"로 처리돼
 * 달력이 다시 안 뜨는 것처럼 보인다. 지우기가 항상 닫힌 상태로
 * 되돌려야 다음 클릭이 다시 "열기"로 동작한다.
 */
function clear() {
  emit('update:modelValue', '')
  open.value = false
}
</script>

<template>
  <div class="flex w-full flex-col gap-1.5">
    <label
      v-if="label"
      :for="fieldId"
      :class="labelOption === 'sustain' ? 'text-14 text-grey-800 font-medium' : 'sr-only'"
    >
      {{ label }}
    </label>

    <PopoverRoot v-model:open="open">
      <PopoverAnchor as-child>
        <div
          :class="cn(
            inputVariants({ variant: 'box', hasError }),
            'justify-between',
            disabled && 'cursor-not-allowed border-grey-300 opacity-60',
            props.class,
          )"
        >
          <!-- 달력 아이콘도 트리거 버튼 안에 넣는다 — 밖에 따로 두면
               아이콘 자체엔 클릭 핸들러가 없어서, 정확히 아이콘 위를
               누르면 아무 반응이 없는 것처럼 보인다(지우기 ×는 여는
               동작과 다른 별개 동작이라 계속 형제로 둔다). -->
          <PopoverTrigger
            :id="fieldId"
            data-slot="date-picker-trigger"
            type="button"
            :disabled="disabled"
            :aria-invalid="hasError"
            :class="cn('flex h-full min-w-0 flex-1 items-center justify-between gap-1.5 text-left outline-none', !modelValue && 'text-grey-700')"
          >
            <span class="min-w-0 truncate">{{ modelValue || effectivePlaceholder }}</span>
            <CalendarIcon v-if="!(modelValue && !disabled)" class="text-grey-500 size-4 shrink-0" />
          </PopoverTrigger>

          <button
            v-if="modelValue && !disabled"
            type="button"
            aria-label="날짜 지우기"
            class="text-grey-600 hover:text-grey-700 shrink-0"
            @click="clear"
          >
            <XIcon class="size-4" />
          </button>
        </div>
      </PopoverAnchor>

      <PopoverPortal>
        <PopoverContent
          data-slot="date-picker-content"
          :side-offset="6"
          align="start"
          class="bg-popover text-popover-foreground border-grey-200 z-[60] rounded-[14px] border p-1 shadow-lg outline-none"
        >
          <Calendar
            :model-value="calendarValue"
            :holidays="holidays"
            @update:model-value="select"
          />
        </PopoverContent>
      </PopoverPortal>
    </PopoverRoot>

    <p v-if="help" :class="cn('text-14', hasError ? 'text-destructive' : 'text-grey-700')">
      {{ help }}
    </p>
  </div>
</template>

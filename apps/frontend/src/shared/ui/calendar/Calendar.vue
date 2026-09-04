<script setup lang="ts">
import type { CalendarDate, DateValue } from '@internationalized/date'
import { getLocalTimeZone, today } from '@internationalized/date'
import { ChevronLeft, ChevronRight } from '@lucide/vue'
import {
  CalendarCell,
  CalendarCellTrigger,
  CalendarGrid,
  CalendarGridBody,
  CalendarGridHead,
  CalendarGridRow,
  CalendarHeadCell,
  CalendarRoot,
} from 'reka-ui'
import { computed, ref, shallowRef, watch } from 'vue'
import { cn } from '@/shared/lib/utils'

const props = withDefaults(defineProps<{
  modelValue?: DateValue
  minValue?: DateValue
  maxValue?: DateValue
  /** ISO 날짜 문자열(YYYY-MM-DD) — 토·일과 별개로 빨간색으로 표시할 날짜.
   * "어떤 날짜가 한국 공휴일인지"는 이 컴포넌트가 모른다 — shared는 업무
   * 개념을 몰라야 한다는 원칙(Badge와 같은 이유)에 따라, 호출하는 쪽이
   * entities/holiday에서 조회해 그대로 넘겨준다. */
  holidays?: string[]
}>(), {
  modelValue: undefined,
  minValue: undefined,
  maxValue: undefined,
  holidays: () => [],
})

const emit = defineEmits<{
  'update:modelValue': [DateValue | undefined]
}>()

const holidaySet = computed(() => new Set(props.holidays))

/**
 * 토요일=파란색, 일요일 또는 공휴일=빨간색. 겹치는 경우(예: 공휴일이
 * 토요일과 겹칠 때) 빨간색이 우선한다 — 일요일·공휴일 판정을 먼저 본다.
 * 요일은 date.toString()(YYYY-MM-DD, 시간대 없음)을 UTC 자정으로 파싱해
 * 구한다 — 로컬 시간대로 파싱하면 자정 근처에서 요일이 하루 밀릴 수 있다.
 */
function dayColorClass(date: DateValue): string {
  const dayOfWeek = new Date(`${date.toString()}T00:00:00Z`).getUTCDay()
  if (dayOfWeek === 0 || holidaySet.value.has(date.toString())) return 'text-red-600'
  if (dayOfWeek === 6) return 'text-blue-600'
  return 'text-grey-900'
}

/**
 * 헤더의 "연도 월" 글자를 눌러 날짜 → 월 → 연도 순으로 한 단계씩
 * 올라간다. 월/연도를 고르면 그만큼 다시 내려와 날짜 격자를 보여준다
 * (연도를 고르면 월 선택으로, 월을 고르면 날짜 격자로).
 *
 * CalendarRoot의 표준 CalendarHeader·CalendarHeading·CalendarPrev·
 * CalendarNext는 "달 단위 이동"만 알고 있어 이 드릴다운에 못 쓴다 —
 * 대신 placeholder(지금 펼쳐 보여주는 달의 기준 날짜)를 직접 들고
 * 있으면서 이전/다음 버튼의 이동 단위(달/해/12년)를 뷰에 따라 바꾼다.
 */
type ViewMode = 'day' | 'month' | 'year'
const viewMode = ref<ViewMode>('day')

/**
 * CalendarDate로 좁혀 둔다(DatePicker.vue가 항상 parseDate()로 만든
 * CalendarDate만 넘긴다) — DateValue는 CalendarDate·CalendarDateTime·
 * ZonedDateTime의 합타입이라, 이 합타입 변수에 .add()/.subtract()/.set()을
 * 쓰면 타입이 세 클래스의 반환 형태가 뒤섞인 애매한 타입으로 좁혀져
 * CalendarRoot의 placeholder에 다시 대입할 때 타입 에러가 난다.
 *
 * shallowRef를 쓴다 — 일반 ref는 템플릿에서 UnwrapRef를 거치면서
 * CalendarDate처럼 private 필드를 가진 클래스 인스턴스를 평범한 객체
 * 구조로 뭉개 버려(getter들을 값으로 펼치면서 클래스 정체성을 잃는다)
 * CalendarRoot가 기대하는 DateValue와 타입이 어긋난다. CalendarDate는
 * 불변 값 객체라 어차피 통째로 교체만 하지 필드를 직접 고치지 않으므로
 * shallowRef가 더 맞는 선택이기도 하다.
 */
const placeholder = shallowRef<CalendarDate>((props.modelValue as CalendarDate | undefined) ?? today(getLocalTimeZone()))
watch(() => props.modelValue, (value) => {
  if (value) placeholder.value = value as CalendarDate
})

const MONTH_LABELS = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']

const YEARS_PER_PAGE = 12
const yearRangeStart = computed(() => Math.floor(placeholder.value.year / YEARS_PER_PAGE) * YEARS_PER_PAGE)
const years = computed(() => Array.from({ length: YEARS_PER_PAGE }, (_, i) => yearRangeStart.value + i))

const headingText = computed(() => {
  if (viewMode.value === 'year') return `${yearRangeStart.value} - ${yearRangeStart.value + YEARS_PER_PAGE - 1}`
  if (viewMode.value === 'month') return `${placeholder.value.year}년`
  return `${placeholder.value.year}년 ${placeholder.value.month}월`
})

function clickHeading() {
  if (viewMode.value === 'day') viewMode.value = 'month'
  else if (viewMode.value === 'month') viewMode.value = 'year'
}

function goPrev() {
  if (viewMode.value === 'day') placeholder.value = placeholder.value.subtract({ months: 1 })
  else if (viewMode.value === 'month') placeholder.value = placeholder.value.subtract({ years: 1 })
  else placeholder.value = placeholder.value.subtract({ years: YEARS_PER_PAGE })
}

function goNext() {
  if (viewMode.value === 'day') placeholder.value = placeholder.value.add({ months: 1 })
  else if (viewMode.value === 'month') placeholder.value = placeholder.value.add({ years: 1 })
  else placeholder.value = placeholder.value.add({ years: YEARS_PER_PAGE })
}

function selectMonth(month: number) {
  placeholder.value = placeholder.value.set({ month })
  viewMode.value = 'day'
}

function selectYear(year: number) {
  placeholder.value = placeholder.value.set({ year })
  viewMode.value = 'month'
}
</script>

<template>
  <!-- 날짜 격자 기준 너비로 고정한다 — 요일 칸 7개 * 36px(w-9) + 좌우
       패딩(px-3, 12px*2) = 276px. 월/연도 선택기로 바뀌어도 이 너비를
       그대로 쓰기 때문에, 뷰를 오갈 때 팝오버 크기가 늘었다 줄었다
       하지 않는다. -->
  <div class="w-[276px]">
    <div class="flex items-center justify-between p-3 pb-0">
      <button
        type="button"
        aria-label="이전"
        class="hover:bg-grey-100 rounded-[8px] p-1.5"
        @click="goPrev"
      >
        <ChevronLeft class="size-4" />
      </button>
      <button
        type="button"
        data-slot="calendar-heading"
        :disabled="viewMode === 'year'"
        class="hover:bg-grey-100 rounded-[6px] px-2 py-1 text-14 font-bold disabled:pointer-events-none"
        @click="clickHeading"
      >
        {{ headingText }}
      </button>
      <button
        type="button"
        aria-label="다음"
        class="hover:bg-grey-100 rounded-[8px] p-1.5"
        @click="goNext"
      >
        <ChevronRight class="size-4" />
      </button>
    </div>

    <div v-if="viewMode === 'month'" data-slot="calendar-month-picker" class="grid grid-cols-3 gap-2 p-3">
      <button
        v-for="(label, i) in MONTH_LABELS"
        :key="label"
        type="button"
        :class="cn(
          'rounded-[10px] py-2 text-14 hover:bg-grey-100',
          placeholder.month === i + 1 ? 'bg-primary font-semibold text-white hover:bg-primary' : 'text-grey-900',
        )"
        @click="selectMonth(i + 1)"
      >
        {{ label }}
      </button>
    </div>

    <div v-else-if="viewMode === 'year'" data-slot="calendar-year-picker" class="grid grid-cols-3 gap-2 p-3">
      <button
        v-for="year in years"
        :key="year"
        type="button"
        :class="cn(
          'rounded-[10px] py-2 text-14 hover:bg-grey-100',
          placeholder.year === year ? 'bg-primary font-semibold text-white hover:bg-primary' : 'text-grey-900',
        )"
        @click="selectYear(year)"
      >
        {{ year }}
      </button>
    </div>

    <CalendarRoot
      v-else
      v-slot="{ grid, weekDays }"
      :model-value="modelValue"
      :placeholder="placeholder"
      :min-value="minValue"
      :max-value="maxValue"
      locale="ko"
      weekday-format="short"
      class="px-3 pb-3"
      @update:model-value="emit('update:modelValue', $event)"
      @update:placeholder="placeholder = $event as CalendarDate"
    >
      <CalendarGrid v-for="month in grid" :key="month.value.toString()" class="mt-3 w-full">
        <CalendarGridHead>
          <CalendarGridRow class="flex">
            <CalendarHeadCell
              v-for="day in weekDays"
              :key="day"
              class="text-grey-500 flex w-9 items-center justify-center text-12 font-medium"
            >
              {{ day }}
            </CalendarHeadCell>
          </CalendarGridRow>
        </CalendarGridHead>
        <CalendarGridBody>
          <CalendarGridRow v-for="(weekDates, i) in month.rows" :key="`week-${i}`" class="mt-1 flex w-full">
            <CalendarCell v-for="weekDate in weekDates" :key="weekDate.toString()" :date="weekDate" class="p-0">
              <CalendarCellTrigger
                v-slot="{ selected, disabled, outsideView, today: isToday }"
                :day="weekDate"
                :month="month.value"
                :data-date="weekDate.toString()"
                class="flex w-9 items-center justify-center"
              >
                <span
                  :class="cn(
                    'flex size-9 items-center justify-center rounded-full text-14 transition-colors',
                    selected
                      ? 'bg-primary font-semibold text-white'
                      : cn('hover:bg-grey-100', dayColorClass(weekDate)),
                    isToday && !selected ? 'ring-primary ring-1' : '',
                    outsideView ? 'opacity-35' : '',
                    disabled ? 'pointer-events-none opacity-30' : '',
                  )"
                >
                  {{ weekDate.day }}
                </span>
              </CalendarCellTrigger>
            </CalendarCell>
          </CalendarGridRow>
        </CalendarGridBody>
      </CalendarGrid>
    </CalendarRoot>
  </div>
</template>

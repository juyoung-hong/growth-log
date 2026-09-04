<script setup lang="ts">
import type { TaskCreate } from '@/shared/api'
import { computed, reactive, ref, watch } from 'vue'
import { useHolidaysStore } from '@/entities/holiday'
import { useTasksStore } from '@/entities/task'
import { ApiError } from '@/shared/api'
import { parseFieldError } from '@/shared/lib/parse-field-error'
import { Button } from '@/shared/ui/button'
import { DatePicker } from '@/shared/ui/date-picker'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog'
import { Input } from '@/shared/ui/input'

/**
 * 등록 전용이다 — Task 수정·삭제는 이번 단계 범위 밖(레벨3 상세 화면의
 * 몫)이라 PersonFormDialog·TaskGroupFormDialog와 달리 edit 모드가 없다.
 * 상태 선택지도 없다 — TaskCreate에 status 필드 자체가 없고, 모든 Task는
 * 항상 `보류`로 시작한다.
 */
const open = defineModel<boolean>('open', { required: true })

const store = useTasksStore()
const holidaysStore = useHolidaysStore()

const form = reactive({
  name: '',
  estimatedDays: '',
  startDate: '',
})

// 달력이 올해·내년을 넘어가는 날짜까지 색으로 구분해 보여줄 필요는
// 크지 않다고 보고 두 해로 범위를 좁혔다 — 그보다 먼 미래로 달력을
// 넘기면 토·일 색만 보이고 공휴일 표시는 안 뜬다.
const thisYear = new Date().getFullYear()
const holidays = computed(() => [
  ...(holidaysStore.byYear[thisYear] ?? []),
  ...(holidaysStore.byYear[thisYear + 1] ?? []),
])

const fieldErrors = reactive({ name: '' })
const submitting = ref(false)

// new Date().toISOString()은 UTC 기준이라 자정 근처엔 하루가 밀릴 수
// 있다 — 로컬 날짜 구성요소를 직접 조합해 브라우저가 보는 "오늘"과
// 맞춘다.
function todayISODate(): string {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

watch(open, (isOpen) => {
  if (!isOpen) return
  fieldErrors.name = ''
  form.name = ''
  form.estimatedDays = ''
  // 시작일을 비워 두면 "언제부터인지 모르는 태스크"가 되어 예상소요일이
  // 있어도 마감일 자동계산이 안 된다. 오늘을 기본값으로 채워 두고,
  // 사용자가 다르게 시작할 계획이면 직접 바꾸게 한다.
  form.startDate = todayISODate()
  holidaysStore.ensure([thisYear, thisYear + 1])
})

async function submit() {
  fieldErrors.name = ''

  // name은 백엔드도 검증하지만, 빈 값으로 왕복 한 번을 굳이 시키지 않는다.
  if (!form.name.trim()) {
    fieldErrors.name = '이름을 입력하세요.'
    return
  }

  // due_date는 이번 단계에서 직접 입력받지 않는다 — start_date와
  // estimated_days가 둘 다 있으면 백엔드가 워킹데이 기준으로 자동
  // 계산한다(calculate_due_date, Phase B).
  const payload: TaskCreate = {
    name: form.name,
    estimated_days: form.estimatedDays ? Number(form.estimatedDays) : null,
    start_date: form.startDate || null,
  }

  submitting.value = true
  try {
    await store.create(payload)
    open.value = false
  }
  catch (e) {
    if (!(e instanceof ApiError)) throw e
    if (e.status === 400) {
      // Task도 지금 name만 형식 검증 대상이다.
      const parsed = parseFieldError(e.detail)
      if (parsed) fieldErrors.name = parsed.message
    }
  }
  finally {
    submitting.value = false
  }
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-md">
      <DialogHeader>
        <DialogTitle class="text-center font-bold">
          새 태스크
        </DialogTitle>
      </DialogHeader>

      <form class="flex flex-col gap-4" @submit.prevent="submit">
        <Input
          v-model="form.name"
          variant="box"
          label="이름"
          label-option="sustain"
          :has-error="!!fieldErrors.name"
          :help="fieldErrors.name"
        />
        <Input
          v-model="form.estimatedDays"
          variant="box"
          type="number"
          label="예상 소요일"
          label-option="sustain"
          suffix="일"
        />
        <DatePicker
          v-model="form.startDate"
          label="시작일"
          label-option="sustain"
          :holidays="holidays"
        />

        <!-- ConfirmDialog·PersonFormDialog·TaskGroupFormDialog와 같은
             방식 — 버튼 두 개가 네 모서리 온전히 둥근 채로 나란히 붙는다. -->
        <div class="grid grid-cols-2 gap-3">
          <Button
            display="full"
            variant="weak"
            color="light"
            :disabled="submitting"
            @click="open = false"
          >
            취소
          </Button>
          <Button
            type="submit"
            display="full"
            :loading="submitting"
          >
            등록
          </Button>
        </div>
      </form>
    </DialogContent>
  </Dialog>
</template>
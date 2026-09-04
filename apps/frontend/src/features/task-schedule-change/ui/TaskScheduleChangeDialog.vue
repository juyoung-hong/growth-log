<script setup lang="ts">
import type { TaskRead, TaskScheduleUpdate } from '@/shared/api'
import { computed, reactive, ref, watch } from 'vue'
import { useHolidaysStore } from '@/entities/holiday'
import { useTaskDetailStore } from '@/entities/task'
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

const props = defineProps<{ task: TaskRead }>()
const open = defineModel<boolean>('open', { required: true })

const store = useTaskDetailStore()
const holidaysStore = useHolidaysStore()

const form = reactive({
  estimatedDays: '',
  startDate: '',
  dueDate: '',
  reason: '',
})

// TaskFormDialog.vue와 같은 이유로 올해·내년으로 범위를 좁힌다.
const thisYear = new Date().getFullYear()
const holidays = computed(() => [
  ...(holidaysStore.byYear[thisYear] ?? []),
  ...(holidaysStore.byYear[thisYear + 1] ?? []),
])

const fieldErrors = reactive({ dueDate: '' })
const submitting = ref(false)

/**
 * 시작일·마감일은 부분 수정이 아니다 — PATCH /tasks/{id}/schedule은
 * 요청에 없는 필드를 null로 간주해 그대로 덮어쓴다(TaskService.
 * change_schedule). 그래서 열릴 때마다 현재 값으로 두 칸을 다 채운다 —
 * 하나만 비워서 보내면 나머지가 조용히 지워진다.
 *
 * estimated_days는 다르다 — 생략하면(null) 서버가 기존 값을 그대로
 * 쓴다. 그래도 편집 중엔 현재 값을 보여주는 편이 자연스러워 똑같이
 * 채워 둔다.
 */
watch(open, (isOpen) => {
  if (!isOpen) return
  fieldErrors.dueDate = ''
  form.estimatedDays = props.task.estimated_days != null ? String(props.task.estimated_days) : ''
  form.startDate = props.task.start_date ?? ''
  form.dueDate = props.task.due_date ?? ''
  form.reason = ''
  holidaysStore.ensure([thisYear, thisYear + 1])
})

async function submit() {
  fieldErrors.dueDate = ''

  const payload: TaskScheduleUpdate = {
    start_date: form.startDate || null,
    due_date: form.dueDate || null,
    estimated_days: form.estimatedDays ? Number(form.estimatedDays) : null,
    reason: form.reason || null,
  }

  submitting.value = true
  try {
    await store.changeSchedule(payload)
    open.value = false
  }
  catch (e) {
    if (!(e instanceof ApiError)) throw e
    if (e.status === 400) {
      // 지금 이 엔드포인트가 낼 수 있는 400은 due_date < start_date뿐이다.
      const parsed = parseFieldError(e.detail)
      if (parsed) fieldErrors.dueDate = parsed.message
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
          일정 변경
        </DialogTitle>
      </DialogHeader>

      <form class="flex flex-col gap-4" @submit.prevent="submit">
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
        <DatePicker
          v-model="form.dueDate"
          label="마감일"
          label-option="sustain"
          :has-error="!!fieldErrors.dueDate"
          :help="fieldErrors.dueDate || '비워두면 예상 소요일(주말·공휴일 제외) 기준으로 자동 계산됩니다.'"
          :holidays="holidays"
        />
        <Input
          v-model="form.reason"
          variant="box"
          multiline
          label="사유"
          label-option="sustain"
          placeholder="예: 담당자 휴가로 순연"
        />

        <div class="grid grid-cols-2 gap-3">
          <Button display="full" variant="weak" color="light" :disabled="submitting" @click="open = false">
            취소
          </Button>
          <Button type="submit" display="full" :loading="submitting">
            저장
          </Button>
        </div>
      </form>
    </DialogContent>
  </Dialog>
</template>
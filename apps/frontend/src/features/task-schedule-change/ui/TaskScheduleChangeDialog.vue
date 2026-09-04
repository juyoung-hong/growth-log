<script setup lang="ts">
import type { TaskRead, TaskScheduleUpdate } from '@/shared/api'
import { reactive, ref, watch } from 'vue'
import { useTaskDetailStore } from '@/entities/task'
import { ApiError } from '@/shared/api'
import { parseFieldError } from '@/shared/lib/parse-field-error'
import { Button } from '@/shared/ui/button'
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

const form = reactive({
  startDate: '',
  dueDate: '',
  reason: '',
})

const fieldErrors = reactive({ dueDate: '' })
const submitting = ref(false)

/**
 * 일정 변경은 부분 수정이 아니다 — PATCH /tasks/{id}/schedule은 요청에
 * 없는 필드를 null로 간주해 그대로 덮어쓴다(TaskService.change_schedule).
 * 그래서 열릴 때마다 현재 값으로 두 칸을 다 채운다 — 하나만 비워서
 * 보내면 나머지가 조용히 지워진다.
 */
watch(open, (isOpen) => {
  if (!isOpen) return
  fieldErrors.dueDate = ''
  form.startDate = props.task.start_date ?? ''
  form.dueDate = props.task.due_date ?? ''
  form.reason = ''
})

async function submit() {
  fieldErrors.dueDate = ''

  const payload: TaskScheduleUpdate = {
    start_date: form.startDate || null,
    due_date: form.dueDate || null,
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
          v-model="form.startDate"
          variant="box"
          type="date"
          label="시작일"
          label-option="sustain"
        />
        <Input
          v-model="form.dueDate"
          variant="box"
          type="date"
          label="마감일"
          label-option="sustain"
          :has-error="!!fieldErrors.dueDate"
          :help="fieldErrors.dueDate || '비워두면 예상 소요일 기준으로 자동 계산됩니다.'"
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
<script setup lang="ts">
import type { Scope, TaskGroupRead, TaskStatus } from '@/shared/api'
import { computed, reactive, ref, watch } from 'vue'
import { useTaskGroupsStore } from '@/entities/task-group'
import { ApiError } from '@/shared/api'
import { parseFieldError } from '@/shared/lib/parse-field-error'
import { TASK_STATUS_BADGE_COLOR, TASK_STATUSES } from '@/shared/lib/task-status'
import { Button } from '@/shared/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog'
import { Input } from '@/shared/ui/input'
import { Tabs, TabsList, TabsTrigger } from '@/shared/ui/tabs'
import { ToggleGroup, ToggleGroupItem } from '@/shared/ui/toggle-group'

/**
 * 등록·수정을 겸한다. entities/person의 PersonFormDialog와 같은 구조다.
 * taskGroup이 있으면 수정, 없으면 등록.
 */
const props = defineProps<{
  taskGroup?: TaskGroupRead | null
}>()

const open = defineModel<boolean>('open', { required: true })

const store = useTaskGroupsStore()

const isEdit = computed(() => props.taskGroup != null)

const form = reactive({
  category: '회사' as Scope,
  status: '진행중' as TaskStatus,
  name: '',
  description: '',
})

const fieldErrors = reactive({ name: '' })
const submitting = ref(false)

watch(open, (isOpen) => {
  if (!isOpen) return
  fieldErrors.name = ''
  form.category = props.taskGroup?.category ?? '회사'
  form.status = props.taskGroup?.status ?? '진행중'
  form.name = props.taskGroup?.name ?? ''
  form.description = props.taskGroup?.description ?? ''
})

async function submit() {
  fieldErrors.name = ''

  // name은 백엔드도 검증하지만, 빈 값으로 왕복 한 번을 굳이 시키지 않는다.
  if (!form.name.trim()) {
    fieldErrors.name = '이름을 입력하세요.'
    return
  }

  const payload = {
    category: form.category,
    status: form.status,
    name: form.name,
    description: form.description || null,
  }

  submitting.value = true
  try {
    if (isEdit.value && props.taskGroup) {
      await store.update(props.taskGroup.id, payload)
    }
    else {
      await store.create(payload)
    }
    open.value = false
  }
  catch (e) {
    if (!(e instanceof ApiError)) throw e
    if (e.status === 400) {
      // TaskGroup은 지금 name만 형식 검증 대상이다 — 다른 필드가
      // 400을 낼 방법이 없으니 field 값을 다시 분기하지 않는다.
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
          {{ isEdit ? '프로젝트 정보 수정' : '새 프로젝트' }}
        </DialogTitle>
      </DialogHeader>

      <form class="flex flex-col gap-4" @submit.prevent="submit">
        <div class="flex flex-col gap-1.5">
          <Tabs v-model="form.category">
            <TabsList size="small" stretch>
              <TabsTrigger value="회사">
                회사
              </TabsTrigger>
              <TabsTrigger value="개인">
                개인
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <div class="flex flex-col gap-1.5">
          <span class="text-14 text-grey-800 font-medium">상태</span>
          <!-- 상태는 목록 카드의 배지와 같은 색으로 보여야 "지금 뭘 고르고
               있는지"가 배지와 바로 연결된다 — Tabs(밑줄) 대신 ToggleGroup을
               쓴 이유는 14-toggle-group.md 참고. -->
          <ToggleGroup v-model="form.status" stretch>
            <ToggleGroupItem
              v-for="status in TASK_STATUSES"
              :key="status"
              :value="status"
              :color="TASK_STATUS_BADGE_COLOR[status]"
            >
              {{ status }}
            </ToggleGroupItem>
          </ToggleGroup>
        </div>

        <Input
          v-model="form.name"
          variant="box"
          label="이름"
          label-option="sustain"
          :has-error="!!fieldErrors.name"
          :help="fieldErrors.name"
        />
        <Input
          v-model="form.description"
          variant="box"
          multiline
          label="설명"
          label-option="sustain"
        />

        <!-- ConfirmDialog·PersonFormDialog와 같은 방식 — 버튼 두 개가
             패널 폭을 꽉 채우며 나란히 붙는다(06-dialog.md 참고). -->
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
            {{ isEdit ? '저장' : '등록' }}
          </Button>
        </div>
      </form>
    </DialogContent>
  </Dialog>
</template>
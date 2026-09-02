<script setup lang="ts">
import type { TaskGroupRead } from '@/shared/api'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskGroupsStore } from '@/entities/task-group'
import { TaskGroupFormDialog } from '@/features/task-group-create'
import { ScopeSwitch } from '@/features/scope-switch'
import { ApiError } from '@/shared/api'
import { parseScopeParam, SCOPE_BADGE_COLOR, toScope } from '@/shared/lib/scope'
import { TASK_STATUS_BADGE_COLOR } from '@/shared/lib/task-status'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Card } from '@/shared/ui/card'
import { ConfirmDialog } from '@/shared/ui/confirm-dialog'
import { Progress } from '@/shared/ui/progress'
import { Separator } from '@/shared/ui/separator'

const route = useRoute()
const router = useRouter()
const scopeParam = computed(() => parseScopeParam(route.query.scope))

const store = useTaskGroupsStore()
const includeArchived = ref(false)

watch(
  [scopeParam, includeArchived],
  ([param, archived]) => store.load({ category: toScope(param), includeArchived: archived }),
  { immediate: true },
)

// "완료 포함"은 서버에 대응 파라미터가 없다 — status 필터는 값 하나만
// 고를 수 있어 "완료만 빼고 전부"를 표현할 수 없다. 그래서 전체를
// 받아온 뒤 여기서 걸러낸다. "보관됨 포함"과 처리 방식이 다르다.
const includeCompleted = ref(false)
const visibleTaskGroups = computed(() =>
  includeCompleted.value
    ? store.taskGroups
    : store.taskGroups.filter(tg => tg.status !== '완료'),
)

const formOpen = ref(false)
const editing = ref<TaskGroupRead | null>(null)

function openCreate() {
  editing.value = null
  formOpen.value = true
}

function openEdit(taskGroup: TaskGroupRead) {
  editing.value = taskGroup
  formOpen.value = true
}

function openDetail(taskGroup: TaskGroupRead) {
  router.push({ name: 'task-group-detail', params: { id: taskGroup.id } })
}

const deleteOpen = ref(false)
const deleteTarget = ref<TaskGroupRead | null>(null)
const deleteError = ref<string | null>(null)
const deleting = ref(false)

function askDelete(taskGroup: TaskGroupRead) {
  deleteTarget.value = taskGroup
  deleteError.value = null
  deleteOpen.value = true
}

// 참조 중이라 막히는 Person과 달리, TaskGroup 삭제는 항상 성공한다
// (백엔드가 하위 태스크·회의록·참고자료를 전부 함께 지운다). 그래서
// 이 경고는 "삭제가 막힐 수 있다"가 아니라 "무엇이 함께 지워지는지"를
// 알리는 데 집중한다 — 목록 응답에 이미 있는 progress.total_tasks를
// 그대로 쓴다(추가 API 호출 없음).
const deleteDescription = computed(() => {
  const taskCount = deleteTarget.value?.progress?.total_tasks ?? 0
  return taskCount > 0
    ? `할일 ${taskCount}개를 포함해 관련된 회의록·참고자료가 모두 함께 삭제됩니다. 되돌릴 수 없습니다.`
    : '삭제하면 되돌릴 수 없습니다.'
})

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  deleteError.value = null
  try {
    await store.remove(deleteTarget.value.id)
    deleteOpen.value = false
  }
  catch (e) {
    if (e instanceof ApiError) {
      deleteError.value = e.detail
    }
    else {
      throw e
    }
  }
  finally {
    deleting.value = false
  }
}
</script>

<template>
  <section class="flex flex-col gap-5">
    <div class="flex items-center justify-between">
      <h1 class="text-22 font-bold">
        할일관리
      </h1>
      <Button size="medium" @click="openCreate">
        + 새 프로젝트
      </Button>
    </div>

    <ScopeSwitch />

    <div class="flex items-center gap-4">
      <label class="text-14 text-grey-700 flex items-center gap-1.5">
        <input v-model="includeCompleted" type="checkbox" class="accent-primary size-4">
        완료 포함
      </label>
      <label class="text-14 text-grey-700 flex items-center gap-1.5">
        <input v-model="includeArchived" type="checkbox" class="accent-primary size-4">
        보관됨 포함
      </label>
    </div>

    <p v-if="store.loading" class="text-15 text-grey-700">
      불러오는 중…
    </p>
    <p v-else-if="visibleTaskGroups.length === 0" class="text-15 text-grey-700">
      표시할 프로젝트가 없습니다.
    </p>

    <div v-else class="flex flex-col gap-3">
      <Card
        v-for="taskGroup in visibleTaskGroups"
        :key="taskGroup.id"
        class="hover:bg-secondary/60 cursor-pointer p-5 transition-colors"
        @click="openDetail(taskGroup)"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-17 text-grey-900 font-semibold">{{ taskGroup.name }}</span>
              <Badge :color="TASK_STATUS_BADGE_COLOR[taskGroup.status]">
                {{ taskGroup.status }}
              </Badge>
            </div>
            <p v-if="taskGroup.description" class="text-15 text-grey-700 mt-1">
              {{ taskGroup.description }}
            </p>
          </div>
          <div class="flex shrink-0 gap-2" @click.stop>
            <Button size="small" variant="weak" color="light" @click="openEdit(taskGroup)">
              수정
            </Button>
            <Button size="small" variant="weak" color="danger" @click="askDelete(taskGroup)">
              삭제
            </Button>
          </div>
        </div>

        <div v-if="taskGroup.progress" class="mt-4 flex items-center gap-3">
          <Progress :model-value="taskGroup.progress.percent" />
          <span class="text-13 text-grey-700 shrink-0 tabular-nums">
            {{ taskGroup.progress.done_tasks }}/{{ taskGroup.progress.total_tasks }} 완료
          </span>
        </div>

        <Separator variant="full" class="my-4" />

        <Badge :color="SCOPE_BADGE_COLOR[taskGroup.category]">
          {{ taskGroup.category }}
        </Badge>
      </Card>
    </div>

    <TaskGroupFormDialog v-model:open="formOpen" :task-group="editing" />

    <ConfirmDialog
      v-model:open="deleteOpen"
      :title="`${deleteTarget?.name ?? ''} 삭제`"
      :description="deleteError ?? deleteDescription"
      confirm-text="삭제"
      danger
      :loading="deleting"
      @confirm="confirmDelete"
    />
  </section>
</template>
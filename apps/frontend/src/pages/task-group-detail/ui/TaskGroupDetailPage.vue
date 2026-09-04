<script setup lang="ts">
import type { TaskGroupRead, TaskStatus } from '@/shared/api'
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { getTaskGroup } from '@/entities/task-group'
import { useTasksStore } from '@/entities/task'
import { TaskCompleteCheckbox } from '@/features/task-complete-toggle'
import { TaskFormDialog } from '@/features/task-create'
import { toScopeParam } from '@/shared/lib/scope'
import { TASK_STATUS_BADGE_COLOR } from '@/shared/lib/task-status'
import { formatTaskSchedule } from '@/shared/lib/task-schedule'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Progress } from '@/shared/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs'

const route = useRoute()
const router = useRouter()
const taskGroupId = computed(() => Number(route.params.id))

function openTask(taskId: number) {
  router.push({ name: 'task-detail', params: { id: taskGroupId.value, taskId } })
}

const taskGroup = ref<TaskGroupRead | null>(null)
const tasksStore = useTasksStore()

/**
 * TaskGroupsPage.vue의 watch(..., { immediate: true }) 패턴을 그대로
 * 쓴다 — onMounted 대신 param을 지켜보면, 나중에 두 상세 화면 사이를
 * 라우터가 컴포넌트를 재사용하며 바로 이동하는 링크가 생겨도(지금은
 * 없다) 다시 안 불러오는 사고를 막는다.
 *
 * 진행률 헤더는 진입 시 한 번만 불러온다 — 태스크를 등록하거나 완료
 * 체크해도 새로고침 전까지 갱신되지 않는다. 실시간으로 반영하려면
 * 레벨3 목록 store와 레벨2 헤더 사이에 새 결합을 만들어야 해서, 이번
 * 단계(목록·생성·완료체크) 범위를 넘어선다고 보고 미뤘다.
 */
watch(taskGroupId, async (id) => {
  taskGroup.value = await getTaskGroup(id)
  await tasksStore.load(id)
}, { immediate: true })

const showAll = ref(false)
const visibleTasks = computed(() => showAll.value ? tasksStore.allTasks : tasksStore.tasks)

// "N건" 대신 상태별로 나눠 보여준다 — 전체보기 여부와 무관하게 이
// 프로젝트의 전체 태스크 상태 분포이므로 allTasks 기준으로 센다.
const statusCounts = computed(() => {
  const counts: Record<TaskStatus, number> = { 보류: 0, 진행중: 0, 완료: 0 }
  for (const task of tasksStore.allTasks) counts[task.status] += 1
  return counts
})

const createOpen = ref(false)
</script>

<template>
  <section v-if="taskGroup" class="flex flex-col gap-5">
    <!-- breadcrumb: 마지막 조각(지금 이 페이지)은 링크가 아니라 굵은
         글자로 둔다 — "여기 있다"는 표시이지 갈 곳이 아니다. -->
    <nav class="text-14 text-grey-700 flex items-center gap-1.5">
      <RouterLink
        :to="{ name: 'task-groups', query: { scope: toScopeParam(taskGroup.category) } }"
        class="hover:text-primary"
      >
        할일관리
      </RouterLink>
      <span class="text-grey-400" aria-hidden="true">›</span>
      <span class="text-grey-900 font-medium">{{ taskGroup.name }}</span>
    </nav>

    <div>
      <div class="flex items-center gap-2">
        <h1 class="text-22 font-bold">
          {{ taskGroup.name }}
        </h1>
        <Badge :color="TASK_STATUS_BADGE_COLOR[taskGroup.status]">
          {{ taskGroup.status }}
        </Badge>
      </div>
      <p v-if="taskGroup.description" class="text-15 text-grey-700 mt-1">
        {{ taskGroup.description }}
      </p>
      <div v-if="taskGroup.progress" class="mt-3 flex max-w-xs items-center gap-3">
        <Progress :model-value="taskGroup.progress.percent" />
        <span class="text-13 text-grey-700 shrink-0 tabular-nums">
          {{ taskGroup.progress.done_tasks }}/{{ taskGroup.progress.total_tasks }} 완료
        </span>
      </div>
    </div>

    <Tabs default-value="tasks">
      <TabsList aria-label="레벨2 상세 탭">
        <TabsTrigger value="tasks">
          할일목록
        </TabsTrigger>
        <TabsTrigger value="meetings">
          회의록
        </TabsTrigger>
        <TabsTrigger value="attachments">
          참고자료
        </TabsTrigger>
      </TabsList>

      <TabsContent value="tasks" class="flex flex-col gap-4">
        <div class="flex items-center justify-between">
          <span class="text-15 text-grey-700 flex items-center gap-2">
            보류 {{ statusCounts.보류 }}건, 진행중 {{ statusCounts.진행중 }}건, 완료 {{ statusCounts.완료 }}건
            <button type="button" class="text-primary font-medium hover:underline" @click="showAll = !showAll">
              {{ showAll ? '기본 보기로 돌아가기' : '전체보기' }}
            </button>
          </span>
          <Button size="medium" @click="createOpen = true">
            + 태스크
          </Button>
        </div>

        <p v-if="tasksStore.loading" class="text-15 text-grey-700">
          불러오는 중…
        </p>
        <p v-else-if="visibleTasks.length === 0" class="text-15 text-grey-700">
          등록된 태스크가 없습니다.
        </p>

        <ul v-else class="flex flex-col gap-2">
          <li
            v-for="task in visibleTasks"
            :key="task.id"
            class="bg-grey-100 hover:bg-grey-200 flex cursor-pointer items-center gap-3 rounded-[10px] px-4 py-3 transition-colors"
            @click="openTask(task.id)"
          >
            <span @click.stop>
              <TaskCompleteCheckbox :task="task" />
            </span>
            <div class="min-w-0 flex-1">
              <span
                class="text-15"
                :class="task.status === '완료' ? 'text-grey-500 line-through' : 'text-grey-900'"
              >
                {{ task.name }}
              </span>
              <p class="text-13 text-grey-700 mt-0.5">
                {{ formatTaskSchedule(task) }}
              </p>
            </div>
            <Badge :color="TASK_STATUS_BADGE_COLOR[task.status]">
              {{ task.status }}
            </Badge>
          </li>
        </ul>
      </TabsContent>

      <TabsContent value="meetings">
        <p class="text-15 text-grey-700">
          다음 단계에서 만듭니다.
        </p>
      </TabsContent>
      <TabsContent value="attachments">
        <p class="text-15 text-grey-700">
          다음 단계에서 만듭니다.
        </p>
      </TabsContent>
    </Tabs>

    <TaskFormDialog v-model:open="createOpen" />
  </section>
</template>
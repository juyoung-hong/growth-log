<script setup lang="ts">
import type { TaskGroupRead } from '@/shared/api'
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useTaskDetailStore } from '@/entities/task'
import { getTaskGroup } from '@/entities/task-group'
import { TaskScheduleChangeDialog } from '@/features/task-schedule-change'
import { TaskStatusToggle } from '@/features/task-status-change'
import { toScopeParam } from '@/shared/lib/scope'
import { formatTaskSchedule } from '@/shared/lib/task-schedule'
import { Button } from '@/shared/ui/button'
import { Separator } from '@/shared/ui/separator'
import { TaskActivityLog } from '@/widgets/task-activity-log'
import { TaskComments } from '@/widgets/task-comments'
import { TaskAssigneeManage } from '@/features/task-assignee-manage'
import { TaskDependencyManage } from '@/features/task-dependency-manage'


const route = useRoute()
const taskId = computed(() => Number(route.params.taskId))

const store = useTaskDetailStore()

// TaskGroupDetailPage.vue와 같은 이유로 immediate watch를 쓴다.
watch(taskId, id => store.load(id), { immediate: true })

// 브레드크럼("할일관리 › 프로젝트 이름 › 태스크 이름")에 쓰려고 태스크가
// 속한 TaskGroup을 별도로 불러온다. task_group_id 기준으로 지켜본다 —
// 상태·일정을 바꿔
// store.task가 다시 채워질 때마다(같은 그룹인데도) 매번 다시 불러오지
// 않기 위해서다. immediate:true를 쓴다 — store.task가 이 컴포넌트보다
// 먼저 채워져 있는 경우(예: 테스트에서 initialState로 미리 심어 둔 경우)
// taskGroupId가 처음부터 값을 갖고 있어 "변화"가 한 번도 안 일어나면
// non-immediate watch는 아예 실행되지 않는다.
const taskGroupId = computed(() => store.task?.task_group_id ?? null)
const taskGroup = ref<TaskGroupRead | null>(null)

watch(taskGroupId, async (id) => {
  if (id == null) return
  taskGroup.value = await getTaskGroup(id)
}, { immediate: true })

const scheduleOpen = ref(false)
</script>

<template>
  <section v-if="store.task" class="flex flex-col gap-6">
    <!-- TaskGroupDetailPage.vue와 같은 브레드크럼. 여긴 두 단계라
         가운데 조각(프로젝트 이름)도 링크다 — 마지막 조각(지금 태스크)만
         굵은 글자로 남긴다. -->
    <nav v-if="taskGroup" class="text-14 text-grey-700 flex items-center gap-1.5">
      <RouterLink
        :to="{ name: 'task-groups', query: { scope: toScopeParam(taskGroup.category) } }"
        class="hover:text-primary"
      >
        할일관리
      </RouterLink>
      <span class="text-grey-400" aria-hidden="true">›</span>
      <RouterLink
        :to="{ name: 'task-group-detail', params: { id: taskGroup.id } }"
        class="hover:text-primary"
      >
        {{ taskGroup.name }}
      </RouterLink>
      <span class="text-grey-400" aria-hidden="true">›</span>
      <span class="text-grey-900 font-medium">{{ store.task.name }}</span>
    </nav>

    <div>
      <h1 class="text-22 font-bold">
        {{ store.task.name }}
      </h1>
      <TaskStatusToggle :task="store.task" class="mt-3" />
    </div>

    <div class="flex items-center justify-between">
      <div>
        <p class="text-14 text-grey-700">
          예상 {{ store.task.estimated_days ?? '-' }}일
        </p>
        <p class="text-14 text-grey-700">
          {{ formatTaskSchedule(store.task) }}
        </p>
      </div>
      <Button size="small" variant="weak" color="light" @click="scheduleOpen = true">
        일정 변경
      </Button>
    </div>

    <Separator variant="full" />

    <TaskAssigneeManage />

    <Separator variant="full" />

    <TaskDependencyManage />

    <Separator variant="full" />

    <TaskActivityLog />

    <Separator variant="full" />

    <TaskComments />

    <TaskScheduleChangeDialog v-model:open="scheduleOpen" :task="store.task" />
  </section>
</template>
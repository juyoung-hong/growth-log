<script setup lang="ts">
import { computed, ref } from 'vue'
import { useTaskDetailStore } from '@/entities/task'
import { usePersonsStore } from '@/entities/person'
import { ApiError } from '@/shared/api'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'

const store = useTaskDetailStore()
const personsStore = usePersonsStore()

const pickerOpen = ref(false)
const query = ref('')
const error = ref('')
const pending = ref(false)

// 회사·개인 구분 없이 전체 인물을 대상으로 검색한다 — 담당자는 어느
// 쪽이든 될 수 있다. 이름 검색 API가 백엔드에 없어(#37 조사 결과)
// 전체 목록을 받아 클라이언트에서 필터링한다.
async function openPicker() {
  error.value = ''
  pickerOpen.value = true
  if (personsStore.persons.length === 0) await personsStore.load()
}

const candidates = computed(() => {
  const assignedIds = new Set(store.assignees.map(p => p.id))
  const q = query.value.trim()
  return personsStore.persons
    .filter(p => !assignedIds.has(p.id))
    .filter(p => !q || p.name.includes(q))
})

async function add(personId: number) {
  pending.value = true
  error.value = ''
  try {
    await store.addAssignee(personId)
    query.value = ''
  }
  catch (e) {
    error.value = e instanceof ApiError ? e.detail : '담당자를 추가하지 못했습니다.'
  }
  finally {
    pending.value = false
  }
}

async function remove(personId: number) {
  pending.value = true
  error.value = ''
  try {
    await store.removeAssignee(personId)
  }
  catch (e) {
    error.value = e instanceof ApiError ? e.detail : '담당자를 제거하지 못했습니다.'
  }
  finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <h2 class="text-17 font-bold">
      담당자
    </h2>

    <p v-if="store.assignees.length === 0 && !pickerOpen" class="text-14 text-grey-700">
      아직 담당자가 없습니다.
    </p>

    <ul v-else class="flex flex-wrap gap-2">
      <li
        v-for="person in store.assignees"
        :key="person.id"
        class="bg-grey-100 text-14 text-grey-900 flex items-center gap-1.5 rounded-full py-1 pl-3 pr-2"
      >
        {{ person.name }}
        <button
          type="button"
          class="text-grey-500 hover:text-grey-900"
          :disabled="pending"
          :aria-label="`${person.name} 담당자에서 제거`"
          @click="remove(person.id)"
        >
          ×
        </button>
      </li>
    </ul>

    <div v-if="pickerOpen" class="flex flex-col gap-2">
      <Input v-model="query" variant="box" placeholder="이름으로 검색" />
      <ul v-if="candidates.length > 0" class="border-grey-200 flex max-h-40 flex-col overflow-y-auto rounded-[10px] border">
        <li v-for="person in candidates" :key="person.id">
          <button
            type="button"
            class="hover:bg-grey-100 text-14 w-full px-3 py-2 text-left disabled:opacity-50"
            :disabled="pending"
            @click="add(person.id)"
          >
            {{ person.name }}
            <span class="text-grey-500 text-13">{{ person.category }}</span>
          </button>
        </li>
      </ul>
      <p v-else class="text-14 text-grey-700">
        검색 결과가 없습니다.
      </p>
    </div>

    <Button size="small" variant="weak" color="light" class="self-start" @click="pickerOpen ? pickerOpen = false : openPicker()">
      {{ pickerOpen ? '닫기' : '+ 담당자' }}
    </Button>

    <p v-if="error" class="text-13 text-destructive">
      {{ error }}
    </p>
  </div>
</template>
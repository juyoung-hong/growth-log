<script setup lang="ts">
import type { PersonRead } from '@/shared/api'
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePersonsStore } from '@/entities/person'
import { PersonFormDialog } from '@/features/person-create'
import { ScopeSwitch } from '@/features/scope-switch'
import { ApiError } from '@/shared/api'
import { parseScopeParam, SCOPE_BADGE_COLOR, toScope } from '@/shared/lib/scope'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { ConfirmDialog } from '@/shared/ui/confirm-dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableEmpty,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui/table'

const route = useRoute()
const scopeParam = computed(() => parseScopeParam(route.query.scope))

const store = usePersonsStore()
watch(scopeParam, param => store.load(toScope(param)), { immediate: true })

const formOpen = ref(false)
const editing = ref<PersonRead | null>(null)

function openCreate() {
  editing.value = null
  formOpen.value = true
}

function openEdit(person: PersonRead) {
  editing.value = person
  formOpen.value = true
}

const deleteOpen = ref(false)
const deleteTarget = ref<PersonRead | null>(null)
const deleteError = ref<string | null>(null)
const deleting = ref(false)

function askDelete(person: PersonRead) {
  deleteTarget.value = person
  deleteError.value = null
  deleteOpen.value = true
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  deleteError.value = null
  try {
    await store.remove(deleteTarget.value.id)
    deleteOpen.value = false
  }
  catch (e) {
    // PersonReferencedError -> 409. 다른 데이터가 참조 중이면 지우지
    // 않고 이유를 그대로 보여준다 — 캐스케이드 삭제가 아니라 삭제 차단이다.
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
      <h1 class="text-22 font-bold">인물관리</h1>
      <Button size="medium" @click="openCreate">
        + 인물 등록
      </Button>
    </div>

    <ScopeSwitch />

    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>이름</TableHead>
          <TableHead>구분</TableHead>
          <TableHead>이메일</TableHead>
          <TableHead>전화번호</TableHead>
          <TableHead>소속</TableHead>
          <TableHead class="text-right">관리</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableEmpty v-if="store.loading" :colspan="6">
          불러오는 중…
        </TableEmpty>
        <TableEmpty v-else-if="store.persons.length === 0" :colspan="6">
          등록된 인물이 없습니다.
        </TableEmpty>
        <TableRow v-for="person in store.persons" :key="person.id">
          <TableCell class="font-medium text-grey-900">
            {{ person.name }}
          </TableCell>
          <TableCell>
            <Badge :color="SCOPE_BADGE_COLOR[person.category]">
              {{ person.category }}
            </Badge>
          </TableCell>
          <TableCell class="text-grey-700">
            {{ person.email ?? '-' }}
          </TableCell>
          <TableCell class="text-grey-700">
            {{ person.phone ?? '-' }}
          </TableCell>
          <TableCell class="text-grey-700">
            {{ person.affiliation ?? '-' }}
          </TableCell>
          <TableCell class="text-right">
            <div class="flex justify-end gap-2">
              <Button size="small" variant="weak" color="light" @click="openEdit(person)">
                수정
              </Button>
              <Button size="small" variant="weak" color="danger" @click="askDelete(person)">
                삭제
              </Button>
            </div>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>

    <PersonFormDialog v-model:open="formOpen" :person="editing" />

    <ConfirmDialog
      v-model:open="deleteOpen"
      :title="`${deleteTarget?.name ?? ''} 삭제`"
      :description="deleteError ?? '삭제하면 되돌릴 수 없습니다.'"
      confirm-text="삭제"
      danger
      :loading="deleting"
      @confirm="confirmDelete"
    />
  </section>
</template>
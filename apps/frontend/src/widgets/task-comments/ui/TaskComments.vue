<script setup lang="ts">
import type { TaskCommentRead } from '@/shared/api'
import { ref } from 'vue'
import { useTaskDetailStore } from '@/entities/task'
import { ApiError } from '@/shared/api'
import { formatDateTime } from '@/shared/lib/format'
import { Button } from '@/shared/ui/button'
import { ConfirmDialog } from '@/shared/ui/confirm-dialog'
import { Input } from '@/shared/ui/input'

const store = useTaskDetailStore()

const newContent = ref('')
const addError = ref('')
const adding = ref(false)

async function add() {
  addError.value = ''
  if (!newContent.value.trim()) {
    addError.value = '내용을 입력하세요.'
    return
  }
  adding.value = true
  try {
    await store.addComment(newContent.value)
    newContent.value = ''
  }
  catch (e) {
    addError.value = e instanceof ApiError ? e.detail : '등록하지 못했습니다.'
  }
  finally {
    adding.value = false
  }
}

// 댓글은 여러 개가 동시에 화면에 떠 있을 수 있어 "지금 고치는 중인
// 댓글"을 id 하나로만 추적한다 — 한 번에 하나만 편집 모드로 둔다.
const editingId = ref<number | null>(null)
const editContent = ref('')
const editError = ref('')
const saving = ref(false)

function startEdit(comment: TaskCommentRead) {
  editingId.value = comment.id
  editContent.value = comment.content
  editError.value = ''
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit(commentId: number) {
  editError.value = ''
  if (!editContent.value.trim()) {
    editError.value = '내용을 입력하세요.'
    return
  }
  saving.value = true
  try {
    await store.editComment(commentId, editContent.value)
    editingId.value = null
  }
  catch (e) {
    editError.value = e instanceof ApiError ? e.detail : '수정하지 못했습니다.'
  }
  finally {
    saving.value = false
  }
}

const deleteOpen = ref(false)
const deleteTargetId = ref<number | null>(null)
const deleting = ref(false)

function askDelete(commentId: number) {
  deleteTargetId.value = commentId
  deleteOpen.value = true
}

async function confirmDelete() {
  if (deleteTargetId.value == null) return
  deleting.value = true
  try {
    await store.removeComment(deleteTargetId.value)
    deleteOpen.value = false
  }
  finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <h2 class="text-17 font-bold">
      댓글
    </h2>

    <p v-if="store.comments.length === 0" class="text-14 text-grey-700">
      아직 댓글이 없습니다.
    </p>

    <ul v-else class="flex flex-col gap-3">
      <li v-for="comment in store.comments" :key="comment.id">
        <template v-if="editingId === comment.id">
          <Input
            v-model="editContent"
            variant="box"
            multiline
            :has-error="!!editError"
            :help="editError"
          />
          <div class="mt-1.5 flex gap-2">
            <Button size="small" :loading="saving" @click="saveEdit(comment.id)">
              저장
            </Button>
            <Button size="small" variant="weak" color="light" :disabled="saving" @click="cancelEdit">
              취소
            </Button>
          </div>
        </template>
        <template v-else>
          <p class="text-14 text-grey-900">
            {{ comment.content }}
          </p>
          <div class="text-13 text-grey-700 mt-0.5 flex items-center gap-2">
            <span class="tabular-nums">{{ formatDateTime(comment.created_at) }}</span>
            <button type="button" class="hover:underline" @click="startEdit(comment)">
              수정
            </button>
            <span>·</span>
            <button type="button" class="hover:underline" @click="askDelete(comment.id)">
              삭제
            </button>
          </div>
        </template>
      </li>
    </ul>

    <div class="flex flex-col gap-2">
      <Input
        v-model="newContent"
        variant="box"
        multiline
        placeholder="댓글 추가…"
        :has-error="!!addError"
        :help="addError"
      />
      <Button size="medium" class="self-end" :loading="adding" @click="add">
        등록
      </Button>
    </div>

    <ConfirmDialog
      v-model:open="deleteOpen"
      title="댓글 삭제"
      description="삭제하면 되돌릴 수 없습니다."
      confirm-text="삭제"
      danger
      :loading="deleting"
      @confirm="confirmDelete"
    />
  </div>
</template>
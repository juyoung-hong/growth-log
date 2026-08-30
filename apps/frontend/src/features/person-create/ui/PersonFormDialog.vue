<script setup lang="ts">
import type { PersonRead, Scope } from '@/shared/api'
import { computed, reactive, ref, watch } from 'vue'
import { parsePersonFieldError, usePersonsStore } from '@/entities/person'
import { ApiError } from '@/shared/api'
import { Button } from '@/shared/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog'
import { Input } from '@/shared/ui/input'

/**
 * 등록·수정을 겸한다. person이 있으면 수정, 없으면 등록 — 화면(pages/persons)이
 * 여는 방식만 다를 뿐 폼 구조와 검증은 완전히 같아서 두 화면으로 나누지 않았다.
 */
const props = defineProps<{
  person?: PersonRead | null
}>()

const open = defineModel<boolean>('open', { required: true })

const store = usePersonsStore()

const isEdit = computed(() => props.person != null)

const form = reactive({
  category: '회사' as Scope,
  name: '',
  email: '',
  phone: '',
  affiliation: '',
})

const fieldErrors = reactive({ name: '', email: '', phone: '' })
const submitting = ref(false)

// 다이얼로그가 열릴 때마다 person 기준으로 폼을 다시 채운다. person이
// 없으면(등록) 빈 값으로, 있으면(수정) 그 값으로. 열려 있는 동안 person이
// 바뀌는 경우는 없어서 open만 지켜보면 된다.
watch(open, (isOpen) => {
  if (!isOpen) return
  fieldErrors.name = ''
  fieldErrors.email = ''
  fieldErrors.phone = ''
  form.category = props.person?.category ?? '회사'
  form.name = props.person?.name ?? ''
  form.email = props.person?.email ?? ''
  form.phone = props.person?.phone ?? ''
  form.affiliation = props.person?.affiliation ?? ''
})

async function submit() {
  fieldErrors.name = ''
  fieldErrors.email = ''
  fieldErrors.phone = ''

  // name은 백엔드도 검증하지만, 빈 값으로 왕복 한 번을 굳이 시키지 않는다.
  if (!form.name.trim()) {
    fieldErrors.name = '이름을 입력하세요.'
    return
  }

  const payload = {
    category: form.category,
    name: form.name,
    email: form.email || null,
    phone: form.phone || null,
    affiliation: form.affiliation || null,
  }

  submitting.value = true
  try {
    if (isEdit.value && props.person) {
      await store.update(props.person.id, payload)
    }
    else {
      await store.create(payload)
    }
    open.value = false
  }
  catch (e) {
    if (!(e instanceof ApiError)) throw e

    // 409는 이 두 엔드포인트에서 이메일 중복 하나뿐이라 바로 email에 건다.
    if (e.status === 409) {
      fieldErrors.email = e.detail
      return
    }
    if (e.status === 400) {
      const parsed = parsePersonFieldError(e.detail)
      if (parsed) fieldErrors[parsed.field] = parsed.message
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
        <DialogTitle>{{ isEdit ? '인물 정보 수정' : '인물 등록' }}</DialogTitle>
      </DialogHeader>

      <form class="flex flex-col gap-4" @submit.prevent="submit">
        <div class="flex gap-2">
          <Button
            size="small"
            :variant="form.category === '회사' ? 'fill' : 'weak'"
            :color="form.category === '회사' ? 'primary' : 'light'"
            @click="form.category = '회사'"
          >
            회사
          </Button>
          <Button
            size="small"
            :variant="form.category === '개인' ? 'fill' : 'weak'"
            :color="form.category === '개인' ? 'primary' : 'light'"
            @click="form.category = '개인'"
          >
            개인
          </Button>
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
          v-model="form.email"
          variant="box"
          type="email"
          label="이메일"
          label-option="sustain"
          :has-error="!!fieldErrors.email"
          :help="fieldErrors.email"
        />
        <Input
          v-model="form.phone"
          variant="box"
          label="전화번호"
          label-option="sustain"
          placeholder="010-1234-5678"
          :has-error="!!fieldErrors.phone"
          :help="fieldErrors.phone"
        />
        <Input
          v-model="form.affiliation"
          variant="box"
          label="소속"
          label-option="sustain"
        />

        <DialogFooter>
          <Button variant="weak" color="light" :disabled="submitting" @click="open = false">
            취소
          </Button>
          <Button type="submit" :loading="submitting">
            {{ isEdit ? '저장' : '등록' }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
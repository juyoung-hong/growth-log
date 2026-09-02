<script setup lang="ts">
import type { PersonRead, Scope } from '@/shared/api'
import { computed, reactive, ref, watch } from 'vue'
import { parsePersonFieldError, usePersonsStore } from '@/entities/person'
import { ApiError } from '@/shared/api'
import { Button } from '@/shared/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog'
import { Input } from '@/shared/ui/input'
import { Tabs, TabsList, TabsTrigger } from '@/shared/ui/tabs'

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
        <!-- ConfirmDialog와 같은 언어: 제목은 볼드·가운데 정렬. -->
        <DialogTitle class="text-center font-bold">
          {{ isEdit ? '인물 정보 수정' : '인물 등록' }}
        </DialogTitle>
      </DialogHeader>

      <form class="flex flex-col gap-4" @submit.prevent="submit">
        <!--
          Button 두 개짜리 토글 대신 Tabs를 쓴다 — 상단 ScopeSwitch가
          같은 회사/개인 선택을 이미 Tabs로 표현하고 있어서, 폼 안에서도
          같은 부품을 쓰는 쪽이 "이건 회사·개인 중 하나를 고르는
          자리"라는 걸 일관되게 전달한다. size="small"만 준다 — 폼
          안이라 ScopeSwitch(size 기본값 large)보다 한 단계 조밀하게.
          stretch로 폭을 꽉 채운다 — 버튼 토글이었을 때 폭을 채웠던
          것과 같은 이유로, 짧은 글자 두 개만 왼쪽에 몰려 있고 나머지가
          빈 공간으로 남는 걸 피한다.
        -->
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

        <!--
          ConfirmDialog와 같은 방식 — DialogFooter(공용 부품, 오른쪽 정렬
          + 보통 크기)를 쓰지 않고, 버튼 두 개가 패널 폭을 꽉 채우며
          나란히 붙는 형태를 직접 구성한다. DialogContent의 p-4 여백은
          그대로 두어(모서리가 잘리지 않게) 버튼 사이에만 간격을 준다.
        -->
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
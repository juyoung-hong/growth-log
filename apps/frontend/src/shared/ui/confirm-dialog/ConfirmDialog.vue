<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { Button } from '@/shared/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog'

/**
 * TDS ConfirmDialog 인터페이스 + Open Color 값.
 * https://tossmini-docs.toss.im/tds-mobile/components/Dialog/confirm-dialog/
 *
 * title·description·cancel·confirm 네 조각으로 이뤄진다. 이 앱의 모든
 * 삭제가 이 하나를 재사용한다. 화면마다 확인창을 따로 만들면 어떤 곳은
 * "정말 삭제할까요?"만 묻고 어떤 곳은 연쇄 삭제를 경고하는 식으로 위험
 * 안내가 들쭉날쭉해지기 때문이다.
 *
 * TDS는 cancelButton/confirmButton을 임의의 버튼 엘리먼트를 통째로 받는
 * 슬롯으로 둔다. 이 구현은 그렇게 하지 않고 텍스트·danger·loading만
 * 받는 좁은 prop으로 고정했다 — 슬롯으로 열어두면 화면마다 버튼을 다르게
 * 구성하게 되어, 이 컴포넌트를 만든 이유(위험 안내 통일)가 무너진다.
 */
const open = defineModel<boolean>('open', { required: true })

const props = withDefaults(
  defineProps<{
    title: string
    description?: string
    confirmText?: string
    cancelText?: string
    /** 되돌릴 수 없는 작업이면 true. 확인 버튼이 빨간색이 된다. */
    danger?: boolean
    loading?: boolean
    /** 딤머를 눌렀을 때(그리고 Escape로) 닫을지. 지정하지 않으면
     * danger일 때만 막는다 — TDS 기본값은 true(닫힘)지만, 되돌릴 수 없는
     * 결정은 실수로 안 닫히는 쪽이 이 앱의 원칙에 맞다. */
    closeOnDimmerClick?: boolean
  }>(),
  {
    description: undefined,
    confirmText: '확인',
    cancelText: '취소',
    danger: false,
    loading: false,
    closeOnDimmerClick: undefined,
  },
)

const emit = defineEmits<{ confirm: []; cancel: [] }>()

const allowImplicitClose = computed(() => props.closeOnDimmerClick ?? !props.danger)

function cancel() {
  open.value = false
  emit('cancel')
}

// 닫히지 않을 때 클릭이 씹힌 건지 의도적으로 막힌 건지 구분되게
// 흔들림으로 알려준다 — TDS ConfirmDialog 문서의 지침이다.
const shaking = ref(false)
function shake() {
  shaking.value = false
  nextTick(() => { shaking.value = true })
  setTimeout(() => { shaking.value = false }, 300)
}

function onInteractOutside(event: Event) {
  if (allowImplicitClose.value) return
  event.preventDefault()
  shake()
}

function onEscapeKeyDown(event: Event) {
  if (allowImplicitClose.value) {
    cancel()
    return
  }
  event.preventDefault()
  shake()
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent
      :show-close-button="false"
      :class="shaking && 'animate-shake'"
      @interact-outside="onInteractOutside"
      @escape-key-down="onEscapeKeyDown"
    >
      <DialogHeader>
        <!-- TDS 기본값(title: grey800·bold / description: grey600·medium)을
             따르되, description 색만 grey700으로 바꿨다. grey600은 흰
             배경과 3.32:1로 WCAG AA(4.5)에 못 미친다 — 02-typography.md에서
             이미 한 번 고친 문제라 여기서 되풀이하지 않는다. 제목·본문
             모두 가운데 정렬하고, 본문(16px)이 버튼 글자(15px)보다
             크게 — 확인창의 메시지가 버튼보다 눈에 먼저 들어와야 한다. -->
        <DialogTitle class="text-20 text-center font-bold text-grey-800">
          {{ title }}
        </DialogTitle>
        <DialogDescription v-if="description" class="text-16 text-center font-medium text-grey-700">
          {{ description }}
        </DialogDescription>
      </DialogHeader>

      <!--
        DialogFooter(공용 부품)를 쓰지 않는다. 그건 폼 다이얼로그처럼
        "오른쪽 정렬된 보통 크기 버튼"에 맞춘 것이고, 확인창은 버튼
        두 개가 패널 폭을 꽉 채우며 나란히 붙는 쪽이 메시지에 눈길이
        먼저 가고 오조작도 줄인다 — TDS ConfirmDialog 참고 레이아웃.
        DialogContent의 p-4 여백은 그대로 두고(모서리가 잘리지 않게)
        버튼 두 개 사이에만 간격을 준다 — 각 버튼은 Button 기본 반지름
        그대로 네 모서리가 온전히 둥글다.
      -->
      <div class="grid grid-cols-2 gap-3">
        <Button
          display="full"
          variant="weak"
          color="dark"
          :disabled="loading"
          @click="cancel"
        >
          {{ cancelText }}
        </Button>
        <Button
          display="full"
          :color="danger ? 'danger' : 'primary'"
          :loading="loading"
          @click="emit('confirm')"
        >
          {{ confirmText }}
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>

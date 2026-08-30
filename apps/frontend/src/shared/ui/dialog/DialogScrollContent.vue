<script setup lang="ts">
import type { DialogContentEmits, DialogContentProps } from 'reka-ui'

import type { HTMLAttributes } from 'vue'
import { XIcon } from '@lucide/vue'
import { reactiveOmit } from '@vueuse/core'
import {
  DialogClose,
  DialogContent,
  DialogPortal,
  useForwardPropsEmits,
} from 'reka-ui'
import { cn } from '@/shared/lib/utils'
import { Button } from '@/shared/ui/button'
import DialogOverlay from './DialogOverlay.vue'

defineOptions({
  inheritAttrs: false,
})

const props = withDefaults(defineProps<DialogContentProps & { class?: HTMLAttributes['class'], showCloseButton?: boolean }>(), {
  showCloseButton: true,
})
const emits = defineEmits<DialogContentEmits>()

const delegatedProps = reactiveOmit(props, 'class')

const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <DialogPortal>
    <!-- DialogOverlay를 그대로 재사용해 딤머 색을 한 곳에서만 관리한다.
         레이아웃(grid+스크롤)만 이 컴포넌트에서 얹는다. -->
    <DialogOverlay class="grid place-items-center overflow-y-auto p-4">
      <DialogContent
        data-slot="dialog-content"
        v-bind="{ ...$attrs, ...forwarded }"
        :class="cn('bg-popover text-popover-foreground data-open:animate-in data-closed:animate-out data-closed:fade-out-0 data-open:fade-in-0 data-closed:zoom-out-95 data-open:zoom-in-95 relative grid w-full max-w-lg gap-4 rounded-lg p-4 text-14 duration-100 outline-none', props.class)"
        @pointer-down-outside="(event) => {
          // 스크롤 가능한 오버레이는 place-items-center로 콘텐츠를 감싼
          // 영역 자체가 클릭 히트박스라, 콘텐츠 바깥 여백을 눌러도
          // 'outside'로 잡힌다. 실제로 카드 테두리 밖을 눌렀을 때만
          // 닫히게, 좌표로 다시 확인한다.
          const originalEvent = event.detail.originalEvent;
          const target = originalEvent.target as HTMLElement;
          if (originalEvent.offsetX > target.clientWidth || originalEvent.offsetY > target.clientHeight) {
            event.preventDefault();
          }
        }"
      >
        <slot />

        <DialogClose
          v-if="showCloseButton"
          data-slot="dialog-close"
          as-child
        >
          <Button variant="weak" color="light" class="absolute top-2 right-2" size="icon">
            <XIcon />
            <span class="sr-only">Close</span>
          </Button>
        </DialogClose>
      </DialogContent>
    </DialogOverlay>
  </DialogPortal>
</template>

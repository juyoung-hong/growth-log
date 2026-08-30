import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'

export { default as Alert } from './Alert.vue'
export { default as AlertAction } from './AlertAction.vue'
export { default as AlertDescription } from './AlertDescription.vue'
export { default as AlertTitle } from './AlertTitle.vue'

/**
 * shadcn의 Alert 하나를 그대로 유지하면서, TDS가 별도 컴포넌트로 둔
 * Toast의 개념(자동 소멸·화면에 뜨는 위치·표시 상태 관리)을 이 컴포넌트에
 * 흡수한다. https://tossmini-docs.toss.im/tds-mobile/components/toast/
 * Input에서 TextField·TextArea·SearchField를 하나로 합친 것과 같은 방식이다
 * (09-input.md 참고) — 컴포넌트 경계는 shadcn 쪽(Alert)을 유지하고,
 * TDS가 별도 문서로 나눠 둔 개념만 prop으로 흡수한다.
 *
 * TDS 사이드바에서 "알림·메시지" 개념에 해당할 만한 컴포넌트를 전부
 * 확인했다 — Toast만 흡수했고 나머지는 흡수하지 않았다. 이유는
 * apps/docs/design/10-alert.md에 있다.
 */
export const alertVariants = cva('grid gap-0.5 rounded-lg border px-2.5 py-2 text-left text-14 has-data-[slot=alert-action]:relative has-data-[slot=alert-action]:pr-18 has-[>svg]:grid-cols-[auto_1fr] has-[>svg]:gap-x-2 *:[svg]:row-span-2 *:[svg]:translate-y-0.5 *:[svg]:text-current *:[svg:not([class*=size-])]:size-4 group/alert relative w-full', {
  variants: {
    variant: {
      default: 'bg-card text-card-foreground',
      destructive: 'text-destructive bg-card *:data-[slot=alert-description]:text-destructive/90 *:[svg]:text-current',
    },
  },
  defaultVariants: {
    variant: 'default',
  },
})

export type AlertVariants = VariantProps<typeof alertVariants>

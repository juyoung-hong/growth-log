import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'

export { default as Tabs } from './Tabs.vue'
export { default as TabsContent } from './TabsContent.vue'
export { default as TabsList } from './TabsList.vue'
export { default as TabsTrigger } from './TabsTrigger.vue'

/**
 * TDS 인터페이스(size/fluid/itemGap/ariaLabel + Tab.Item의 selected/redBean)
 * + Open Color 값.
 * https://tossmini-docs.toss.im/tds-mobile/components/tab/
 *
 * TDS는 size/fluid/itemGap/ariaLabel을 전부 루트(Tab)에 둔다. 이 구현은
 * Root(Tabs)/List(TabsList)/Trigger(TabsTrigger) 세 계층으로 나뉘어 있어,
 * 실제 탭 목록의 시각적 컨테이너인 TabsList에 옮겼다 — "탭 목록 전체의
 * 크기·간격·스크롤 여부"라는 의미상 TabsList가 맞는 자리다.
 *
 * shadcn 원본은 default(세그먼트 배경)/line(밑줄) 두 variant를 뒀는데,
 * TDS Tab 문서에는 그런 선택지 자체가 없다 — 밑줄 하나뿐이다. 그래서
 * variant 축을 없애고 밑줄 스타일 하나로 고정했다. selected 표시는
 * Reka UI의 값 매칭(data-state)으로 이미 되고 있어 TDS의 boolean
 * `selected` prop을 따로 만들지 않았다 — 03-button.md의 `as`와 같은 이유다.
 */
export const tabsListVariants = cva(
  // relative + after:로 목록 전체 폭을 가로지르는 회색 기준선을 하나 깐다.
  // 탭마다 따로 밑줄을 그리면 탭 사이 간격(gap)에서 선이 끊겨 보인다 —
  // 기준선을 목록 쪽에 한 번만 그리고, 선택된 탭의 파란 강조선(TabsTrigger)이
  // 그 위에 겹치게 해서 하나로 이어진 선처럼 보이게 한다.
  'group/tabs-list relative inline-flex w-fit shrink-0 items-center after:absolute after:inset-x-0 after:bottom-0 after:h-0.5 after:rounded-full after:bg-grey-200',
  {
    variants: {
      size: {
        large: 'h-11',
        small: 'h-9',
      },
      // TDS: 4개 넘으면 fluid로 가로 스크롤을 켜라는 지침. 기본(false)은
      // 스크롤을 안 만든다 — 넘치면 그대로 넘쳐서 "여기 fluid가 필요하다"는
      // 신호가 눈에 보이게 둔다. 조용히 줄바꿈되면 그 신호를 놓친다.
      fluid: {
        true: 'flex-nowrap overflow-x-auto',
        false: 'flex-nowrap',
      },
    },
    defaultVariants: {
      size: 'large',
      fluid: false,
    },
  },
)

export type TabsListVariants = VariantProps<typeof tabsListVariants>

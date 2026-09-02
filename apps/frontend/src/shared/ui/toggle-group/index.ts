import type { BadgeVariants } from '@/shared/ui/badge'

export { default as ToggleGroup } from './ToggleGroup.vue'
export { default as ToggleGroupItem } from './ToggleGroupItem.vue'

/**
 * TDS 원본에는 없는, 이 프로젝트가 새로 더한 컴포넌트다. Tabs와 생김새는
 * 비슷해 보이지만 쓰임이 다르다 — Tabs는 "화면(패널)을 바꾸는 내비게이션"이고,
 * ToggleGroup은 "폼 안에서 값 하나를 고르는 입력"이다. 값 선택기라는 점에서
 * Reka UI의 RadioGroup(값 하나만 고르는 라디오 그룹) 위에 만들었다 —
 * 방향키 이동·`role="radio"` 접근성이 공짜로 딸려온다.
 *
 * 선택된 항목의 색은 Badge의 weak 배합(100단계 배경 + 900단계 글자)을
 * 그대로 재사용한다 — "상태를 고르는 곳"과 "고른 상태를 보여주는 곳"의
 * 색이 갈리면 그 자체가 혼동이기 때문이다(task-group-create의 상태 선택
 * 요구사항). Badge의 badgeVariants()를 직접 호출하지 않고 색 값만 여기
 * 별도 맵으로 옮겨 적은 이유는, badgeVariants가 함께 반환하는 크기·모양
 * 클래스(h-6·rounded-[6px]·font-semibold 등)가 버튼 크기의 항목과 맞지
 * 않아서다. 또한 Tailwind는 `data-[state=checked]:bg-${color}-100`처럼
 * 런타임에 조립한 문자열을 인식하지 못한다 — 스캐너가 읽을 수 있도록
 * 색상별 전체 클래스 문자열을 코드에 그대로 적어 둬야 한다.
 */
export const TOGGLE_GROUP_ITEM_COLOR: Record<NonNullable<BadgeVariants['color']>, string> = {
  blue: 'data-[state=checked]:bg-blue-100 data-[state=checked]:text-blue-900',
  red: 'data-[state=checked]:bg-red-100 data-[state=checked]:text-red-900',
  pink: 'data-[state=checked]:bg-pink-100 data-[state=checked]:text-pink-900',
  purple: 'data-[state=checked]:bg-purple-100 data-[state=checked]:text-purple-900',
  violet: 'data-[state=checked]:bg-violet-100 data-[state=checked]:text-violet-900',
  indigo: 'data-[state=checked]:bg-indigo-100 data-[state=checked]:text-indigo-900',
  cyan: 'data-[state=checked]:bg-cyan-100 data-[state=checked]:text-cyan-900',
  teal: 'data-[state=checked]:bg-teal-100 data-[state=checked]:text-teal-900',
  green: 'data-[state=checked]:bg-green-100 data-[state=checked]:text-green-900',
  lime: 'data-[state=checked]:bg-lime-100 data-[state=checked]:text-lime-900',
  yellow: 'data-[state=checked]:bg-yellow-100 data-[state=checked]:text-yellow-900',
  orange: 'data-[state=checked]:bg-orange-100 data-[state=checked]:text-orange-900',
  grey: 'data-[state=checked]:bg-grey-100 data-[state=checked]:text-grey-900',
}

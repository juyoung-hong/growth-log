import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'

export { default as Badge } from './Badge.vue'

/**
 * TDS 인터페이스(variant/size/color) + Open Color 값.
 * https://tossmini-docs.toss.im/tds-mobile/components/badge/
 *
 * TDS 원본 인터페이스는 이 세 축이 전부다 — 다른 prop은 문서에 없다.
 *   variant : "fill" | "weak"
 *   size    : "xsmall" | "small" | "medium" | "large"
 *   color   : "blue" | "teal" | "green" | "red" | "yellow" | "elephant"
 * 이 구현은 세 축 구조를 그대로 따르되, `color`는 TDS의 6색으로 좁히지
 * 않고 이 프로젝트의 팔레트(01-colors.md) 13색 전부를 지원한다 —
 * "우리 컬러셋"이 TDS보다 넓으니, Badge도 그 전체를 쓸 수 있어야 한다.
 * `elephant`는 01-colors.md의 이름 규칙에 따라 `grey`로 옮겼다.
 *
 * Badge는 상태 라벨이지 액션이 아니다 — hover나 클릭 스타일을 넣지 않는다.
 *
 * fill은 "흰 글자와 4.5:1을 넘기는 가장 얕은 단계 + 흰 글자"가 원칙이고,
 * weak는 "100단계 배경 + 같은 계열 900단계 글자"가 원칙이다. 13색 전부
 * 예외 없이 이 공식을 쓴다 — green·lime·yellow·orange는 900단계로도
 * 4.5:1을 못 넘기지만(아래 괄호), 색마다 규칙이 갈리면 "이 색은 왜
 * 다르지"를 계속 따져야 하는 비용이 대비 수치 하나보다 크다고 판단했다.
 * 대비가 실제로 문제가 되는 자리(예: 저장공간 경고 배너)는 Badge를 쓰지
 * 않고 그 자리에 맞는 색을 새로 고른다(theme.css의 --color-warning-*).
 *
 * 어떤 상태가 어떤 색인지(진행중=blue 같은 것)는 여기서 정하지 않는다.
 * shared는 업무 개념을 몰라야 하므로, 그 매핑은 entities 레이어가 갖는다.
 *
 * radius는 6px을 직접 적는다. rounded-md를 쓰면 theme의 --radius가 카드용
 * 20px 기준이라 18px이 나와서 배지가 알약처럼 보인다.
 */
export const badgeVariants = cva(
  'inline-flex w-fit shrink-0 items-center justify-center gap-1 overflow-hidden whitespace-nowrap rounded-[6px] font-semibold [&>svg]:pointer-events-none [&>svg]:size-3',
  {
    variants: {
      variant: { fill: '', weak: '' },
      color: {
        blue: '',
        red: '',
        pink: '',
        purple: '',
        violet: '',
        indigo: '',
        cyan: '',
        teal: '',
        green: '',
        lime: '',
        yellow: '',
        orange: '',
        grey: '',
      },
      size: {
        // xsmall은 04-typography.md의 text-11(11px/16.5px 행간)을 쓴다.
        // 배지 높이(18px)가 행간보다 살짝 커야 글자가 위아래로 안 잘린다.
        xsmall: 'h-[18px] px-1 text-11',
        small: 'h-5 px-1.5 text-13',
        medium: 'h-6 px-2 text-13',
        large: 'h-7 px-2.5 text-15',
      },
    },
    // 괄호 안은 실측한 명도 대비비(WCAG 기준 4.5:1). fill은 색마다 필요한
    // 최소 단계가 다르다 — 팔레트의 명도 분포가 색상마다 다르기 때문이다.
    compoundVariants: [
      { variant: 'fill', color: 'blue', class: 'bg-blue-800 text-white' }, //     5.02
      { variant: 'fill', color: 'red', class: 'bg-red-800 text-white' }, //       4.51
      { variant: 'fill', color: 'pink', class: 'bg-pink-700 text-white' }, //     4.62
      { variant: 'fill', color: 'purple', class: 'bg-purple-700 text-white' }, // 4.85
      { variant: 'fill', color: 'violet', class: 'bg-violet-600 text-white' }, // 4.95
      { variant: 'fill', color: 'indigo', class: 'bg-indigo-700 text-white' }, // 4.98
      { variant: 'fill', color: 'cyan', class: 'bg-cyan-900 text-white' }, //     5.59
      { variant: 'fill', color: 'teal', class: 'bg-teal-900 text-white' }, //     5.00
      { variant: 'fill', color: 'grey', class: 'bg-grey-700 text-white' }, //     8.18
      // green·lime·yellow·orange는 가장 진한 900단계로도 흰 글자와 4.5를
      // 못 넘긴다. grey900으로 바꾸지 않고 "900 배경 + 흰 글자" 원칙을
      // 색상 예외 없이 지키는 쪽을 택했다.
      { variant: 'fill', color: 'green', class: 'bg-green-900 text-white' }, //   4.37 — AA 미달, 원칙 우선
      { variant: 'fill', color: 'lime', class: 'bg-lime-900 text-white' }, //     3.69 — AA 미달, 원칙 우선
      { variant: 'fill', color: 'yellow', class: 'bg-yellow-900 text-white' }, // 3.00 — AA 미달, 원칙 우선
      { variant: 'fill', color: 'orange', class: 'bg-orange-900 text-white' }, // 4.30 — AA 미달, 원칙 우선

      // weak는 13색 전부 "100단계 배경 + 같은 계열 900단계 글자"로 통일한다.
      { variant: 'weak', color: 'blue', class: 'bg-blue-100 text-blue-900' }, //       4.93
      { variant: 'weak', color: 'red', class: 'bg-red-100 text-red-900' }, //          4.51
      { variant: 'weak', color: 'pink', class: 'bg-pink-100 text-pink-900' }, //       5.80
      { variant: 'weak', color: 'purple', class: 'bg-purple-100 text-purple-900' }, // 5.59
      { variant: 'weak', color: 'violet', class: 'bg-violet-100 text-violet-900' }, // 5.39
      { variant: 'weak', color: 'indigo', class: 'bg-indigo-100 text-indigo-900' }, // 5.34
      { variant: 'weak', color: 'cyan', class: 'bg-cyan-100 text-cyan-900' }, //       4.77
      { variant: 'weak', color: 'teal', class: 'bg-teal-100 text-teal-900' }, //       4.33 — AA 미달, 원칙 우선
      { variant: 'weak', color: 'grey', class: 'bg-grey-100 text-grey-900' }, //       13.87
      { variant: 'weak', color: 'green', class: 'bg-green-100 text-green-900' }, //    3.81 — AA 미달, 원칙 우선
      { variant: 'weak', color: 'lime', class: 'bg-lime-100 text-lime-900' }, //       3.33 — AA 미달, 원칙 우선
      { variant: 'weak', color: 'yellow', class: 'bg-yellow-100 text-yellow-900' }, //  2.69 — AA 미달, 원칙 우선
      { variant: 'weak', color: 'orange', class: 'bg-orange-100 text-orange-900' }, //  3.62 — AA 미달, 원칙 우선
    ],
    defaultVariants: {
      variant: 'weak',
      color: 'grey',
      size: 'medium',
    },
  },
)

export type BadgeVariants = VariantProps<typeof badgeVariants>

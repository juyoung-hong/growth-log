import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'

export { default as Button } from './Button.vue'

/**
 * TDS 규칙(fill/weak × primary/danger/light/dark) + Open Color 값.
 *
 * Open Color는 TDS보다 전반적으로 밝은 팔레트라 흰 글자를 얹으려면
 * 500단계가 아니라 800단계까지 내려가야 WCAG AA(4.5:1)를 만족한다.
 * 아래 각 조합 옆 숫자는 실측한 명도 대비비다.
 *
 * weak의 hover/active는 색에 관계없이 "배경을 한 단계(100->200) 진하게"로
 * 통일한다. primary/danger는 이렇게 하면 같은 계열 900 글자와의 대비가
 * 4.5 밑으로 떨어지지만(blue 4.02, red 3.76), 색마다 hover 방식이 다르면
 * ("이 색은 밑줄, 저 색은 배경 진하게") 그 자체가 또 다른 비일관성이라
 * 대비보다 상호작용 방식의 통일을 우선했다 — green·yellow에서 이미 쓴
 * 것과 같은 판단 기준이다.
 */
export const buttonVariants = cva(
  'group/button shrink-0 items-center justify-center gap-1.5 whitespace-nowrap border border-transparent bg-clip-padding font-bold transition-all outline-none select-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:pointer-events-none not-data-loading:disabled:opacity-40 [&_svg]:pointer-events-none [&_svg]:shrink-0',
  {
    variants: {
      variant: { fill: '', weak: '' },
      color: { primary: '', danger: '', light: '', dark: '' },
      // TDS는 inline(다른 요소와 나란히) / block(자기 줄을 차지하지만
      // 너비는 내용만큼) / full(부모 너비를 꽉 채움) 세 가지를 쓴다.
      // inline-flex를 base에서 여기로 옮겼다 — display에 따라
      // inline-flex/flex가 갈리기 때문이다.
      display: {
        inline: 'inline-flex',
        block: 'flex',
        full: 'flex w-full',
      },
      size: {
        small: 'h-8 rounded-[8px] px-3 text-13 [&_svg:not([class*=size-])]:size-4',
        medium: 'h-[38px] rounded-[10px] px-4 text-15 [&_svg:not([class*=size-])]:size-4',
        large: 'h-12 rounded-[14px] px-5 text-17 [&_svg:not([class*=size-])]:size-5',
        xlarge: 'h-14 rounded-[16px] px-6 text-17 [&_svg:not([class*=size-])]:size-5',
        icon: 'size-[38px] rounded-[10px] [&_svg:not([class*=size-])]:size-4',
      },
    },
    compoundVariants: [
      // fill: 배경이 진할수록 대비가 오르므로 hover/active를 한 단계씩 더 진하게 둔다.
      { variant: 'fill', color: 'primary', class: 'bg-blue-800 text-white hover:bg-blue-900 active:bg-blue-900' }, // 5.02 / hover 6.09
      { variant: 'fill', color: 'danger', class: 'bg-red-800 text-white hover:bg-red-900 active:bg-red-900' }, //     4.51 / hover 5.46
      { variant: 'fill', color: 'light', class: 'bg-grey-100 text-grey-900 hover:bg-grey-200 active:bg-grey-300' }, // 13.87 — 글자색이 배경과 무관해 hover 단계 제약 없음
      // dark는 이미 가장 어두운 900이 기본이라 hover/active는 반대로 밝아진다.
      { variant: 'fill', color: 'dark', class: 'bg-grey-900 text-white hover:bg-grey-800 active:bg-grey-700' }, //    15.43 / 11.51 / 8.18

      // weak: 100단계 배경 + 900단계 글자, hover/active는 배경을 한 단계
      // 더 진하게. primary/danger는 hover 대비가 4.5 밑으로 떨어지지만
      // (아래 괄호) 상호작용 방식의 일관성을 대비 수치보다 우선했다.
      { variant: 'weak', color: 'primary', class: 'bg-blue-100 text-blue-900 hover:bg-blue-200 active:bg-blue-200' }, // 4.93 / hover·active 4.02 — AA 미달, 원칙 우선
      { variant: 'weak', color: 'danger', class: 'bg-red-100 text-red-900 hover:bg-red-200 active:bg-red-200' }, //     4.51 / hover·active 3.76 — AA 미달, 원칙 우선
      { variant: 'weak', color: 'light', class: 'bg-transparent text-grey-700 hover:bg-grey-100 active:bg-grey-100' }, // 8.18(기본) / hover·active 7.35
      { variant: 'weak', color: 'dark', class: 'bg-grey-100 text-grey-800 hover:bg-grey-200 active:bg-grey-200' }, //   10.34 / hover·active 9.70
    ],
    // TDS 기본은 xlarge지만 그건 모바일 하단 전체너비 CTA 기준이다.
    // 데스크톱 화면에서는 medium을 기본으로 두고 주요 CTA에만 large를 준다.
    defaultVariants: {
      variant: 'fill',
      color: 'primary',
      display: 'inline',
      size: 'medium',
    },
  },
)

export type ButtonVariants = VariantProps<typeof buttonVariants>

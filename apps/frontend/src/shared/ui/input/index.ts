import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'

export { default as Input } from './Input.vue'

/**
 * shadcn의 Input 하나를 그대로 유지하면서, TDS가 별도 컴포넌트로 나눠 둔
 * 세 개념(TextField·TextArea·SearchField)을 이 컴포넌트 하나로 흡수한다.
 * https://tossmini-docs.toss.im/tds-mobile/components/TextField/text-field/
 * https://tossmini-docs.toss.im/tds-mobile/components/TextField/text-area/
 * https://tossmini-docs.toss.im/tds-mobile/components/search-field/
 *
 * shadcn 생태계에서 "Input"은 한 줄이든 여러 줄이든, 검색이든 아니든
 * 전부 아우르는 더 큰 개념이다. TDS처럼 컴포넌트를 쪼개지 않고,
 * `multiline` 하나로 <input>/<textarea>를 오가게 했다 — 파일이 여러 개로
 * 늘어나면 셋이 같은 색·라벨·에러 규칙을 공유한다는 사실이 코드에서
 * 안 보이게 된다.
 *
 * 테두리 색이 grey-600인 이유: --border 토큰(grey-200)은 흰 배경과
 * 1.19:1로, 입력 영역의 경계처럼 WCAG 비텍스트 기준(3.0:1)이 적용되는
 * 자리엔 못 미친다. 3.0을 넘기는 가장 얕은 단계를 썼다.
 */
export const inputVariants = cva(
  'flex w-full items-center gap-1.5 border-grey-600 transition-colors has-[:focus]:border-primary has-[:disabled]:cursor-not-allowed has-[:disabled]:border-grey-300 has-[:disabled]:opacity-60',
  {
    variants: {
      variant: {
        box: 'rounded-[10px] border px-3 text-15',
        line: 'rounded-none border-0 border-b px-0.5 text-15',
        big: 'rounded-[14px] border px-4 text-17',
        hero: 'rounded-[16px] border px-4 text-20',
      },
      // 한 줄 입력은 고정 높이(TextField), 여러 줄은 최소 높이로 늘어난다
      // (TextArea) — 나머지(테두리·모서리·글자 크기)는 variant가 그대로
      // 결정하고, 여기서는 높이 모델만 갈린다. items-stretch(기본값)를
      // 그대로 둬서 textarea가 wrapper의 min-h까지 채워지게 한다.
      multiline: {
        false: '',
        true: 'py-2',
      },
      hasError: {
        true: 'border-destructive has-[:focus]:border-destructive',
        false: '',
      },
    },
    compoundVariants: [
      { multiline: false, variant: 'box', class: 'h-[38px]' },
      { multiline: false, variant: 'line', class: 'h-[38px]' },
      { multiline: false, variant: 'big', class: 'h-12' },
      { multiline: false, variant: 'hero', class: 'h-14' },
      { multiline: true, variant: 'box', class: 'min-h-24' },
      { multiline: true, variant: 'line', class: 'min-h-24' },
      { multiline: true, variant: 'big', class: 'min-h-32' },
      { multiline: true, variant: 'hero', class: 'min-h-40' },
    ],
    defaultVariants: {
      multiline: false,
      hasError: false,
    },
  },
)

export type InputVariants = VariantProps<typeof inputVariants>

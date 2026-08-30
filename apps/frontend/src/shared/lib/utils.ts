import type { ClassValue } from "clsx"
import { clsx } from "clsx"
import { extendTailwindMerge } from "tailwind-merge"

/**
 * theme.css는 Tailwind 기본 text-sm/text-base 대신 text-11~text-30이라는
 * 숫자 스케일을 쓴다(02-typography.md). tailwind-merge는 이 커스텀 스케일을
 * 모른 채로 쓰면 text-14/text-16처럼 인식 못 하는 숫자 접미사를 애매한
 * 그룹으로 묶어서, 글자 크기와 글자 색을 함께 오버라이드할 때(예:
 * cn('... text-14 ... text-grey-700', 'text-16 ...')) 겹치는 값 취급을
 * 해 버려 둘 중 하나가 조용히 사라진다 — ConfirmDialog에서 본문을
 * text-16으로 키우면서 실제로 겪은 문제다.
 *
 * theme.text 스케일에 이 숫자들을 등록해서 크기 충돌과 색 충돌을 서로
 * 다른 그룹으로 정확히 분리한다.
 */
const twMerge = extendTailwindMerge({
  extend: {
    theme: {
      text: Array.from({ length: 20 }, (_, i) => String(i + 11)), // 11~30
    },
  },
})

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

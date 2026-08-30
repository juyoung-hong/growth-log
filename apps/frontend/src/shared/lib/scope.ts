import type { Scope } from '@/shared/api'
import type { BadgeVariants } from '@/shared/ui/badge'

/**
 * 개인/회사 구분값의 URL 표기와 API 표기를 오간다.
 *
 * 백엔드 enum은 '회사'/'개인' 한글이라 URL에 그대로 쓰면 인코딩돼 읽기 어렵다.
 * URL에는 영문을 쓰고 API를 부를 때만 한글로 바꾼다.
 */

export const SCOPE_PARAMS = ['company', 'personal'] as const

export type ScopeParam = (typeof SCOPE_PARAMS)[number]

export const SCOPE_BADGE_COLOR: Record<Scope, BadgeVariants['color']> = {
  '회사': 'blue',
  '개인': 'purple',
}

const PARAM_TO_SCOPE: Record<ScopeParam, Scope> = {
  company: '회사',
  personal: '개인',
}

/** 화면에 보여줄 이름. 지금은 API 값과 같지만 바뀔 수 있어 따로 둔다. */
export const SCOPE_LABELS: Record<ScopeParam, string> = {
  company: '회사',
  personal: '개인',
}

export function isScopeParam(value: unknown): value is ScopeParam {
  return SCOPE_PARAMS.includes(value as ScopeParam)
}

/** URL 표기 -> API 표기. */
export function toScope(param: ScopeParam): Scope {
  return PARAM_TO_SCOPE[param]
}

/**
 * 쿼리 파라미터를 안전한 ScopeParam으로 좁힌다.
 * 값이 없거나 이상하면 기본값 'company'로 떨어뜨린다 —
 * 사용자가 URL을 직접 고쳤을 때 화면이 깨지지 않게 하려는 것.
 */
export function parseScopeParam(value: unknown): ScopeParam {
  return isScopeParam(value) ? value : 'company'
}
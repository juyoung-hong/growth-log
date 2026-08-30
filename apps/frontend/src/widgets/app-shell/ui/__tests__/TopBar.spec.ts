import type { StorageUsageRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import TopBar from '../TopBar.vue'

// storage store의 id는 use-storage-usage.ts의 defineStore('storage-usage', ...) 그대로다.
async function mountTopBar(usage: StorageUsageRead | null = null) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
  })
  await router.push('/persons')
  return mount(TopBar, {
    global: {
      plugins: [
        router,
        createTestingPinia({
          stubActions: true,
          createSpy: vi.fn,
          initialState: { 'storage-usage': { usage, loading: false, failed: false } },
        }),
      ],
    },
  })
}

const usage: StorageUsageRead = {
  checked_at: '2026-08-30T00:00:00Z',
  db: { used_bytes: 1, limit_bytes: 100, percent: 1 },
  object_storage: { used_bytes: 1, limit_bytes: 100, percent: 1 },
  warnings: [],
}

describe('topBar', () => {
  it('로고는 "성장일기" 텍스트와 함께 홈("/")으로 가는 링크다', async () => {
    const wrapper = await mountTopBar()
    const logo = wrapper.find('a')
    expect(logo.attributes('href')).toBe('/')
    expect(logo.text()).toContain('성장일기')
  })

  it('로그인 버튼은 아직 비활성화 상태다 — 인증을 붙이기 전까지', async () => {
    const wrapper = await mountTopBar()
    const button = wrapper.find('button')
    expect(button.text()).toBe('로그인')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('usage가 없으면 게이지를 그리지 않는다', async () => {
    const wrapper = await mountTopBar(null)
    expect(wrapper.text()).not.toContain('DB')
    expect(wrapper.text()).not.toContain('파일')
  })

  it('usage가 있으면 DB·파일 게이지를 그린다', async () => {
    const wrapper = await mountTopBar(usage)
    expect(wrapper.text()).toContain('DB')
    expect(wrapper.text()).toContain('파일')
  })
})

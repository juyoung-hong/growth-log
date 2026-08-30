import type { StorageUsageRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import AppShell from '../AppShell.vue'

async function mountShell(usage: StorageUsageRead | null = null) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
  })
  await router.push('/persons')
  return mount(AppShell, {
    slots: { default: '<div>본문 내용</div>' },
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

function withWarnings(warnings: string[]): StorageUsageRead {
  return {
    checked_at: '2026-08-30T00:00:00Z',
    db: { used_bytes: 90, limit_bytes: 100, percent: 90 },
    object_storage: { used_bytes: 1, limit_bytes: 100, percent: 1 },
    warnings,
  }
}

describe('appShell', () => {
  it('슬롯 내용을 본문에 그린다', async () => {
    const wrapper = await mountShell()
    expect(wrapper.text()).toContain('본문 내용')
  })

  it('경고가 없으면 경고 배너를 그리지 않는다', async () => {
    const wrapper = await mountShell(withWarnings([]))
    expect(wrapper.text()).not.toContain('임계치를 넘었습니다')
  })

  it('경고가 있으면 사람이 읽을 수 있는 이름과 함께 배너를 보여준다', async () => {
    const wrapper = await mountShell(withWarnings(['db']))
    expect(wrapper.text()).toContain('데이터베이스')
    expect(wrapper.text()).toContain('임계치를 넘었습니다')
  })

  it('db·object_storage 둘 다 경고면 두 이름을 함께 보여준다', async () => {
    const wrapper = await mountShell(withWarnings(['db', 'object_storage']))
    expect(wrapper.text()).toContain('데이터베이스 · 파일 저장소')
  })

  it('알 수 없는 경고 키는 라벨 매핑 대신 키 이름 그대로 보여준다', async () => {
    const wrapper = await mountShell(withWarnings(['unknown_quota']))
    expect(wrapper.text()).toContain('unknown_quota')
  })
})

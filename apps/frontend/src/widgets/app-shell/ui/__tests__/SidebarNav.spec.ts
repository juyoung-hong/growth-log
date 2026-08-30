import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import SidebarNav from '../SidebarNav.vue'

async function mountAt(path: string) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
  })
  await router.push(path)
  return mount(SidebarNav, { global: { plugins: [router] } })
}

function linkFor(wrapper: Awaited<ReturnType<typeof mountAt>>, label: string) {
  return wrapper.findAll('a').find(a => a.text() === label)
}

describe('sidebarNav', () => {
  it('현재 경로와 정확히 같은 메뉴가 활성화된다', async () => {
    const wrapper = await mountAt('/persons')
    expect(linkFor(wrapper, '인물관리')?.classes()).toContain('bg-accent')
  })

  it('하위 경로에서도 상위 메뉴가 활성화된다', async () => {
    // 태스크 상세(/task-groups/3/tasks/7)는 '할일관리' 메뉴 아래의 화면이다.
    const wrapper = await mountAt('/task-groups/3/tasks/7')
    expect(linkFor(wrapper, '할일관리')?.classes()).toContain('bg-accent')
  })

  it('관련 없는 메뉴는 활성화되지 않는다', async () => {
    const wrapper = await mountAt('/persons')
    expect(linkFor(wrapper, '할일관리')?.classes()).not.toContain('bg-accent')
    expect(linkFor(wrapper, '저장공간')?.classes()).not.toContain('bg-accent')
  })

  it('경로가 접두어만 같고 실제로는 다른 메뉴면 활성화되지 않는다', async () => {
    // '/persons-archive'는 '/persons'로 시작하지만 다른 화면이다.
    // startsWith(`${to}/`)처럼 슬래시까지 확인해야 이런 오탐이 안 생긴다.
    const wrapper = await mountAt('/persons-archive')
    expect(linkFor(wrapper, '인물관리')?.classes()).not.toContain('bg-accent')
  })
})

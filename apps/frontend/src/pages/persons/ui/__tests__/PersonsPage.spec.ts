import type { PersonRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { DOMWrapper, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { usePersonsStore } from '@/entities/person'
import { ApiError } from '@/shared/api'
import PersonsPage from '../PersonsPage.vue'

vi.mock('vue-router', () => ({ useRoute: () => ({ query: {} }) }))

const person: PersonRead = {
  id: 1,
  category: '회사',
  name: '홍주영',
  email: 'hjy@example.com',
  phone: null,
  affiliation: '개발팀',
}

function mountPage(persons: PersonRead[] = [], loading = false) {
  const wrapper = mount(PersonsPage, {
    attachTo: document.body,
    global: {
      // ScopeSwitch는 회사/개인 탭 전환이라는 별개의 관심사라 stub한다 —
      // 안 그러면 그 컴포넌트가 쓰는 useRouter()까지 이 테스트가 신경써야 한다.
      stubs: { ScopeSwitch: true },
      plugins: [
        createTestingPinia({
          stubActions: true,
          createSpy: vi.fn,
          initialState: { persons: { persons, loading } },
        }),
      ],
    },
  })
  return { wrapper, page: new DOMWrapper(document.body) }
}

describe('personsPage', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  it('불러오는 중이면 로딩 문구를 보여준다', () => {
    const { page } = mountPage([], true)
    expect(page.text()).toContain('불러오는 중')
  })

  it('목록이 비어 있으면 안내 문구를 보여준다', () => {
    const { page } = mountPage([], false)
    expect(page.text()).toContain('등록된 인물이 없습니다.')
  })

  it('인물을 행으로 그리고, 없는 값은 -로 보여준다', () => {
    const { page } = mountPage([person])
    expect(page.text()).toContain('홍주영')
    expect(page.text()).toContain('회사')
    expect(page.text()).toContain('hjy@example.com')
    expect(page.text()).toContain('개발팀')
    // phone은 null이었다
    const row = page.find('tbody tr')
    expect(row.text()).toContain('-')
  })

  it('"+ 인물 등록"을 누르면 등록 폼이 person 없이 열린다', async () => {
    const { page } = mountPage([person])
    const createButton = page.findAll('button').find(b => b.text().includes('인물 등록'))
    await createButton?.trigger('click')
    await nextTick()

    expect(page.text()).toContain('인물 등록')
    // 수정 모드였다면 입력창에 '홍주영'이 채워져 있었을 것이다.
    const nameInput = page.find('form input')
    expect((nameInput.element as HTMLInputElement).value).toBe('')
  })

  it('"수정"을 누르면 그 인물의 값으로 폼이 채워진다', async () => {
    const { page } = mountPage([person])
    const editButton = page.findAll('button').find(b => b.text() === '수정')
    await editButton?.trigger('click')
    await nextTick()

    const nameInput = page.find('form input')
    expect((nameInput.element as HTMLInputElement).value).toBe('홍주영')
  })

  it('삭제 확인 후 store.remove를 호출한다', async () => {
    const { page } = mountPage([person])
    const store = usePersonsStore()
    vi.mocked(store.remove).mockResolvedValue(undefined)

    const deleteButton = page.findAll('button').find(b => b.text() === '삭제')
    await deleteButton?.trigger('click')
    await nextTick()

    // ConfirmDialog의 확인 버튼 — 행의 삭제 버튼과 텍스트가 같아, 뒤에 렌더링된(=나중에 찾히는) 쪽을 쓴다.
    const confirmButtons = page.findAll('button').filter(b => b.text() === '삭제')
    await confirmButtons[confirmButtons.length - 1]?.trigger('click')
    await nextTick()
    await nextTick()

    expect(store.remove).toHaveBeenCalledWith(1)
  })

  it('삭제가 참조 중(409)으로 막히면 확인창이 닫히지 않고 이유가 보인다', async () => {
    const { page } = mountPage([person])
    const store = usePersonsStore()
    vi.mocked(store.remove).mockRejectedValue(
      new ApiError(409, '다른 데이터에서 참조 중이라 삭제할 수 없습니다.'),
    )

    const deleteButton = page.findAll('button').find(b => b.text() === '삭제')
    await deleteButton?.trigger('click')
    await nextTick()

    const confirmButtons = page.findAll('button').filter(b => b.text() === '삭제')
    await confirmButtons[confirmButtons.length - 1]?.trigger('click')
    await nextTick()
    await nextTick()

    expect(page.text()).toContain('다른 데이터에서 참조 중이라 삭제할 수 없습니다.')
  })
})
import type { PersonRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { DOMWrapper, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { usePersonsStore } from '@/entities/person'
import { ApiError } from '@/shared/api'
import PersonFormDialog from '../PersonFormDialog.vue'

/**
 * Dialog는 reka-ui의 <Teleport>로 실제 내용을 document.body 바로 아래에
 * 옮긴다 — mount()가 반환하는 wrapper의 DOM 트리 밖이라 wrapper.find()로는
 * 찾을 수 없다. attachTo: document.body로 붙인 뒤, body 전체를 감싸는
 * DOMWrapper로 찾는다. 텔레포트가 자리를 잡는 데 한 틱이 걸려서 nextTick을
 * 기다려야 한다.
 *
 * open:false로 먼저 마운트하고 나서 true로 바꾸는 이유 — PersonFormDialog의
 * 폼 채우기는 watch(open, ...)(immediate 없음)라 "닫힘 -> 열림"이라는
 * 변화가 있어야 실행된다. 실제 화면(pages/persons)도 항상 formOpen이
 * false로 시작해서 버튼을 눌러야 true가 되므로, 처음부터 open:true로
 * 마운트하면 실제 사용 흐름과 달라져 폼이 안 채워진 채로 테스트하게 된다.
 */
async function mountDialog(person: PersonRead | null = null) {
  const wrapper = mount(PersonFormDialog, {
    attachTo: document.body,
    props: { open: false, person },
    global: {
      plugins: [createTestingPinia({ stubActions: true, createSpy: vi.fn })],
    },
  })
  await wrapper.setProps({ open: true })
  await nextTick()
  return { wrapper, page: new DOMWrapper(document.body) }
}

// [이름, 이메일, 전화번호, 소속] 순서로 <input>이 렌더링된다. Input.vue가
// 아직 테스트용 식별자(data-testid 등)를 노출하지 않아 순서로 찾는다 —
// Input에 식별자가 생기면 이 인덱스 접근을 그걸로 바꾸는 게 낫다.
const FIELD = { name: 0, email: 1, phone: 2, affiliation: 3 } as const

describe('personFormDialog', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  it('등록 모드에서는 빈 폼과 "인물 등록" 제목을 보여준다', async () => {
    const { page } = await mountDialog(null)
    expect(page.text()).toContain('인물 등록')
    const inputs = page.findAll('input')
    expect(inputs[FIELD.name]?.element.value).toBe('')
  })

  it('수정 모드에서는 기존 값으로 채워진다', async () => {
    const person: PersonRead = {
      id: 1,
      category: '개인',
      name: '홍주영',
      email: 'hjy@example.com',
      phone: '010-1234-5678',
      affiliation: null,
    }
    const { page } = await mountDialog(person)
    expect(page.text()).toContain('인물 정보 수정')
    const inputs = page.findAll('input')
    expect(inputs[FIELD.name]?.element.value).toBe('홍주영')
    expect(inputs[FIELD.email]?.element.value).toBe('hjy@example.com')
    expect(inputs[FIELD.phone]?.element.value).toBe('010-1234-5678')
  })

  it('이름 없이 제출하면 네트워크를 타지 않고 에러만 보여준다', async () => {
    const { page } = await mountDialog(null)
    const store = usePersonsStore()

    await page.find('form').trigger('submit')

    expect(store.create).not.toHaveBeenCalled()
    expect(page.text()).toContain('이름을 입력하세요.')
  })

  it('등록에 성공하면 store.create를 호출하고 다이얼로그를 닫는다', async () => {
    const { wrapper, page } = await mountDialog(null)
    const store = usePersonsStore()
    vi.mocked(store.create).mockResolvedValue(undefined as never)

    await page.findAll('input')[FIELD.name]?.setValue('김도현')
    await page.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    expect(store.create).toHaveBeenCalledWith({
      category: '회사',
      name: '김도현',
      email: null,
      phone: null,
      affiliation: null,
    })
    // open이 v-model이라, 닫힐 때 부모에게 update:open(false)를 emit한다.
    expect(wrapper.emitted('update:open')).toContainEqual([false])
  })

  it('이메일 중복(409)이면 이메일 칸에 에러를 걸고 다이얼로그는 안 닫는다', async () => {
    const { wrapper, page } = await mountDialog(null)
    const store = usePersonsStore()
    vi.mocked(store.create).mockRejectedValue(new ApiError(409, '이미 등록된 이메일입니다.'))

    await page.findAll('input')[FIELD.name]?.setValue('김도현')
    await page.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    expect(page.text()).toContain('이미 등록된 이메일입니다.')
    expect(wrapper.emitted('update:open')).toBeUndefined()
  })

  it('전화번호 형식(400)이면 전화번호 칸에 에러를 건다', async () => {
    const { page } = await mountDialog(null)
    const store = usePersonsStore()
    vi.mocked(store.create).mockRejectedValue(
      new ApiError(400, 'phone: 전화번호는 하이픈을 포함해야 합니다(예: 010-1234-5678): 01011112222'),
    )

    await page.findAll('input')[FIELD.name]?.setValue('김도현')
    await page.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    expect(page.text()).toContain('전화번호는 하이픈을 포함해야 합니다')
  })
})
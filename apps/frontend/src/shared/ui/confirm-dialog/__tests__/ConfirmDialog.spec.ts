import { DOMWrapper, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'
import { nextTick } from 'vue'
import ConfirmDialog from '../ConfirmDialog.vue'

// Dialog는 Teleport로 document.body에 그려진다 — 09-persons 가이드의
// PersonFormDialog 테스트와 같은 이유로 attachTo + DOMWrapper를 쓴다.
async function mountConfirm(props: Record<string, unknown>) {
  const wrapper = mount(ConfirmDialog, {
    attachTo: document.body,
    props: { open: false, title: '홍주영 삭제', ...props },
  })
  await wrapper.setProps({ open: true })
  await nextTick()
  return { wrapper, page: new DOMWrapper(document.body) }
}

describe('confirmDialog', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  it('제목·본문을 가운데 정렬로 보여준다', async () => {
    const { page } = await mountConfirm({ description: '삭제하면 되돌릴 수 없습니다.' })
    const title = page.find('h2, [data-slot=dialog-title]')
    const description = page.find('[data-slot=dialog-description]')
    expect(title.classes()).toContain('text-center')
    expect(description.classes()).toContain('text-center')
  })

  it('본문 글자가 버튼 글자보다 크다', async () => {
    const { page } = await mountConfirm({ description: '삭제하면 되돌릴 수 없습니다.' })
    const description = page.find('[data-slot=dialog-description]')
    // 버튼은 size 기본값(medium)이라 text-15다. 본문은 text-16이어야
    // "버튼 글씨보다 팝업 글씨가 크다"는 요구가 실제로 지켜진다.
    expect(description.classes()).toContain('text-16')
  })

  it('버튼 두 개가 네 모서리 모두 둥근 채로 간격을 두고 나란히 자리한다', async () => {
    const { page } = await mountConfirm({})
    const buttons = page.findAll('button')
    expect(buttons).toHaveLength(2)

    // 모서리를 잘라내지 않는다 — Button 기본 rounded-[10px]가 그대로 남아야 한다.
    const [cancelBtn, confirmBtn] = buttons
    expect(cancelBtn?.classes()).toContain('rounded-[10px]')
    expect(confirmBtn?.classes()).toContain('rounded-[10px]')

    const footer = cancelBtn?.element.parentElement
    expect(footer?.className).toContain('gap-3')
  })

  it('취소를 누르면 열림 상태가 꺼지고 cancel을 emit한다', async () => {
    const { wrapper, page } = await mountConfirm({})
    const cancelButton = page.findAll('button')[0]
    await cancelButton?.trigger('click')

    expect(wrapper.emitted('cancel')).toHaveLength(1)
    expect(wrapper.emitted('update:open')).toContainEqual([false])
  })

  it('확인을 누르면 confirm만 emit하고 스스로 닫지 않는다 — 닫는 시점은 호출자가 정한다', async () => {
    const { wrapper, page } = await mountConfirm({})
    const confirmButton = page.findAll('button')[1]
    await confirmButton?.trigger('click')

    expect(wrapper.emitted('confirm')).toHaveLength(1)
    expect(wrapper.emitted('update:open')).toBeUndefined()
  })

  it('danger일 때는 Escape로 닫히지 않고 흔들림 클래스가 잠깐 붙는다', async () => {
    const { wrapper, page } = await mountConfirm({ danger: true })

    await page.find('[data-slot=dialog-content]').trigger('keydown', { key: 'Escape' })
    await nextTick()

    expect(wrapper.emitted('update:open')).toBeUndefined()
    expect(page.find('[data-slot=dialog-content]').classes()).toContain('animate-shake')
  })
})

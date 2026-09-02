import { createTestingPinia } from '@pinia/testing'
import { DOMWrapper, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { useTasksStore } from '@/entities/task'
import { ApiError } from '@/shared/api'
import TaskFormDialog from '../TaskFormDialog.vue'

/**
 * TaskGroupFormDialog.spec.ts와 같은 이유로 attachTo + DOMWrapper +
 * open:false -> true 순서를 쓴다(Dialog의 Teleport, 지연 watch).
 */
async function mountDialog() {
  const wrapper = mount(TaskFormDialog, {
    attachTo: document.body,
    props: { open: false },
    global: {
      plugins: [createTestingPinia({ stubActions: true, createSpy: vi.fn })],
    },
  })
  await wrapper.setProps({ open: true })
  await nextTick()
  return { wrapper, page: new DOMWrapper(document.body) }
}

describe('taskFormDialog', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  it('제목은 "새 태스크"이고 빈 폼으로 열린다', async () => {
    const { page } = await mountDialog()
    expect(page.text()).toContain('새 태스크')
    const nameInput = page.findAll('input')[0]
    expect(nameInput?.element.value).toBe('')
  })

  it('상태 선택지가 없다 — Task는 항상 보류로 시작한다', async () => {
    const { page } = await mountDialog()
    expect(page.findAll('[role=tab], [role=radio]')).toHaveLength(0)
  })

  it('시작일을 비워두면 오늘 날짜가 기본값으로 채워진다', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 7, 18, 10, 0, 0))
    try {
      const { page } = await mountDialog()
      const startDateInput = page.findAll('input')[2]
      expect(startDateInput?.element.value).toBe('2026-08-18')
    }
    finally {
      vi.useRealTimers()
    }
  })

  it('이름 없이 제출하면 네트워크를 타지 않고 에러만 보여준다', async () => {
    const { page } = await mountDialog()
    const store = useTasksStore()

    await page.find('form').trigger('submit')

    expect(store.create).not.toHaveBeenCalled()
    expect(page.text()).toContain('이름을 입력하세요.')
  })

  it('예상소요일·시작일을 채우면 숫자·문자열로 변환해 제출한다', async () => {
    const { page } = await mountDialog()
    const store = useTasksStore()
    vi.mocked(store.create).mockResolvedValue(undefined as never)

    const inputs = page.findAll('input')
    await inputs[0]?.setValue('새 태스크')
    await inputs[1]?.setValue('4')
    await inputs[2]?.setValue('2026-08-18')
    await page.find('form').trigger('submit')
    await nextTick()

    expect(store.create).toHaveBeenCalledWith({
      name: '새 태스크',
      estimated_days: 4,
      start_date: '2026-08-18',
    })
  })

  it('등록에 성공하면 다이얼로그를 닫는다', async () => {
    const { wrapper, page } = await mountDialog()
    const store = useTasksStore()
    vi.mocked(store.create).mockResolvedValue(undefined as never)

    await page.findAll('input')[0]?.setValue('새 태스크')
    await page.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    expect(wrapper.emitted('update:open')).toContainEqual([false])
  })

  it('이름 형식 400 에러가 오면 이름 칸에 에러를 걸고 다이얼로그는 안 닫는다', async () => {
    const { wrapper, page } = await mountDialog()
    const store = useTasksStore()
    vi.mocked(store.create).mockRejectedValue(new ApiError(400, 'name: 비어있을 수 없습니다.'))

    await page.findAll('input')[0]?.setValue('a')
    await page.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    expect(page.text()).toContain('비어있을 수 없습니다.')
    expect(wrapper.emitted('update:open')).toBeUndefined()
  })
})
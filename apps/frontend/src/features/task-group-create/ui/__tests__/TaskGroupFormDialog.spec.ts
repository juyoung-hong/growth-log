import type { TaskGroupRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { DOMWrapper, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { useTaskGroupsStore } from '@/entities/task-group'
import { ApiError } from '@/shared/api'
import TaskGroupFormDialog from '../TaskGroupFormDialog.vue'

/**
 * PersonFormDialog.spec.ts와 같은 이유로 attachTo + DOMWrapper +
 * open:false -> true 순서를 쓴다(Dialog의 Teleport, 지연 watch).
 */
async function mountDialog(taskGroup: TaskGroupRead | null = null) {
  const wrapper = mount(TaskGroupFormDialog, {
    attachTo: document.body,
    props: { open: false, taskGroup },
    global: {
      plugins: [createTestingPinia({ stubActions: true, createSpy: vi.fn })],
    },
  })
  await wrapper.setProps({ open: true })
  await nextTick()
  return { wrapper, page: new DOMWrapper(document.body) }
}

const sample: TaskGroupRead = {
  id: 1,
  category: '개인',
  name: '메일서버 이중화',
  description: '기존 단일 메일서버를 이중화한다',
  status: '보류',
  is_archived: false,
  created_at: '2026-08-01T00:00:00Z',
  progress: { total_tasks: 10, done_tasks: 7, percent: 70 },
}

describe('taskGroupFormDialog', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  it('등록 모드에서는 빈 폼과 "새 프로젝트" 제목을 보여준다', async () => {
    const { page } = await mountDialog(null)
    expect(page.text()).toContain('새 프로젝트')
    const nameInput = page.findAll('input')[0]
    expect(nameInput?.element.value).toBe('')
  })

  it('수정 모드에서는 기존 값으로 채워진다', async () => {
    const { page } = await mountDialog(sample)
    expect(page.text()).toContain('프로젝트 정보 수정')
    const inputs = page.findAll('input')
    expect(inputs[0]?.element.value).toBe('메일서버 이중화')
    const textarea = page.find('textarea')
    expect(textarea.element.value).toBe('기존 단일 메일서버를 이중화한다')
  })

  it('이름 없이 제출하면 네트워크를 타지 않고 에러만 보여준다', async () => {
    const { page } = await mountDialog(null)
    const store = useTaskGroupsStore()

    await page.find('form').trigger('submit')

    expect(store.create).not.toHaveBeenCalled()
    expect(page.text()).toContain('이름을 입력하세요.')
  })

  it('상태 선택에서 "완료"를 고르면 그 값으로 제출된다', async () => {
    const { page } = await mountDialog(null)
    const store = useTaskGroupsStore()
    vi.mocked(store.create).mockResolvedValue(undefined as never)

    // 상태는 ToggleGroup(Reka RadioGroup) — 탭과 달리 클릭으로 선택된다.
    const doneOption = page.findAll('[role=radio]').find(t => t.text() === '완료')
    await doneOption?.trigger('click')
    await page.findAll('input')[0]?.setValue('새 프로젝트')
    await page.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    expect(store.create).toHaveBeenCalledWith(expect.objectContaining({
      status: '완료',
      category: '회사',
      name: '새 프로젝트',
    }))
  })

  it('등록에 성공하면 다이얼로그를 닫는다', async () => {
    const { wrapper, page } = await mountDialog(null)
    const store = useTaskGroupsStore()
    vi.mocked(store.create).mockResolvedValue(undefined as never)

    await page.findAll('input')[0]?.setValue('새 프로젝트')
    await page.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    expect(wrapper.emitted('update:open')).toContainEqual([false])
  })

  it('이름 형식 400 에러가 오면 이름 칸에 에러를 걸고 다이얼로그는 안 닫는다', async () => {
    const { wrapper, page } = await mountDialog(null)
    const store = useTaskGroupsStore()
    vi.mocked(store.create).mockRejectedValue(new ApiError(400, 'name: 비어있을 수 없습니다.'))

    await page.findAll('input')[0]?.setValue('a')
    await page.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    expect(page.text()).toContain('비어있을 수 없습니다.')
    expect(wrapper.emitted('update:open')).toBeUndefined()
  })
})
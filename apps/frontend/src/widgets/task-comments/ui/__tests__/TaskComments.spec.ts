import type { TaskCommentRead } from '@/shared/api'
import { createTestingPinia } from '@pinia/testing'
import { DOMWrapper, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { useTaskDetailStore } from '@/entities/task'
import TaskComments from '../TaskComments.vue'

// format.spec.ts와 같은 이유로 로컬 Date를 만들어 toISOString()으로
// 뒤집는다 — 실행 환경의 시간대가 뭐든 formatDateTime이 다시 같은
// 로컬 값으로 돌려놓으므로 테스트가 시간대에 의존하지 않는다.
const createdAtLocal = new Date(2026, 7, 16, 9, 40, 0)
const comment: TaskCommentRead = {
  id: 1, task_id: 1, content: 'TTL 300으로 SPF 값 재확인 필요',
  created_at: createdAtLocal.toISOString(), updated_at: createdAtLocal.toISOString(),
}

// ConfirmDialog(삭제 확인)가 Teleport로 그려지므로 PersonFormDialog.spec.ts와
// 같은 이유로 attachTo + DOMWrapper를 쓴다.
function mountWidget(comments: TaskCommentRead[] = []) {
  const wrapper = mount(TaskComments, {
    attachTo: document.body,
    global: {
      plugins: [createTestingPinia({
        stubActions: true, createSpy: vi.fn,
        initialState: { 'task-detail': { comments } },
      })],
    },
  })
  return { wrapper, page: new DOMWrapper(document.body) }
}

describe('taskComments', () => {
  beforeEach(() => { document.body.innerHTML = '' })

  it('댓글 내용과 등록 시각을 보여준다', () => {
    const { page } = mountWidget([comment])
    expect(page.text()).toContain('TTL 300으로 SPF 값 재확인 필요')
    expect(page.text()).toContain('08-16 09:40')
  })

  it('빈 내용으로 등록하면 네트워크를 타지 않는다', async () => {
    const { page } = mountWidget([])
    const store = useTaskDetailStore()

    const addButton = page.findAll('button').find(b => b.text() === '등록')
    await addButton?.trigger('click')

    expect(store.addComment).not.toHaveBeenCalled()
    expect(page.text()).toContain('내용을 입력하세요.')
  })

  it('수정을 누르면 편집 모드로 바뀌고, 저장하면 editComment를 호출한다', async () => {
    const { page } = mountWidget([comment])
    const store = useTaskDetailStore()
    vi.mocked(store.editComment).mockResolvedValue(undefined as never)

    const editButton = page.findAll('button, [type=button]').find(b => b.text() === '수정')
    await editButton?.trigger('click')

    await page.find('textarea').setValue('고친 내용')
    const saveButton = page.findAll('button').find(b => b.text() === '저장')
    await saveButton?.trigger('click')
    await nextTick()

    expect(store.editComment).toHaveBeenCalledWith(1, '고친 내용')
  })

  it('삭제를 누르면 확인창이 뜨고, 확인하면 removeComment를 호출한다', async () => {
    const { page } = mountWidget([comment])
    const store = useTaskDetailStore()
    vi.mocked(store.removeComment).mockResolvedValue(undefined as never)

    const deleteButton = page.findAll('button, [type=button]').find(b => b.text() === '삭제')
    await deleteButton?.trigger('click')
    await nextTick()

    expect(page.text()).toContain('댓글 삭제')

    const confirmButtons = page.findAll('button').filter(b => b.text() === '삭제')
    await confirmButtons[confirmButtons.length - 1]?.trigger('click')
    await nextTick()
    await nextTick()

    expect(store.removeComment).toHaveBeenCalledWith(1)
  })
})
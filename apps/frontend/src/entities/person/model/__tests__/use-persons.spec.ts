import type { PersonRead } from '@/shared/api'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '@/shared/api'
import { createPerson } from '../../api/create-person'
import { deletePerson } from '../../api/delete-person'
import { listPersons } from '../../api/list-persons'
import { updatePerson } from '../../api/update-person'
import { usePersonsStore } from '../use-persons'

// api 함수 자체(fetch·URL 조립)는 STEP 1에서 이미 타입으로 검증했다.
// 여기서는 store의 로직 — "언제 무엇을 다시 부르는가", "에러를 어떻게
// 흘려보내는가" — 만 본다. 그래서 HTTP 계층이 아니라 이 경계를 mock한다.
vi.mock('../../api/create-person')
vi.mock('../../api/delete-person')
vi.mock('../../api/list-persons')
vi.mock('../../api/update-person')

const person: PersonRead = {
  id: 1,
  category: '회사',
  name: '홍주영',
  email: null,
  phone: null,
  affiliation: null,
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.clearAllMocks() // mock 호출 기록은 테스트 사이에 저절로 안 비워진다
  vi.mocked(listPersons).mockResolvedValue([person])
})

describe('usePersonsStore', () => {
  it('load가 성공하면 persons를 채운다', async () => {
    const store = usePersonsStore()
    await store.load('회사')
    expect(store.persons).toEqual([person])
    expect(listPersons).toHaveBeenCalledWith('회사')
  })

  it('load가 끝나기 전까지 loading이 true다', async () => {
    const store = usePersonsStore()
    const promise = store.load()
    expect(store.loading).toBe(true)
    await promise
    expect(store.loading).toBe(false)
  })

  it('create 성공 후 마지막으로 불렀던 필터로 다시 읽는다', async () => {
    const store = usePersonsStore()
    await store.load('개인') // 화면이 "개인" 탭을 보고 있는 상황을 흉내낸다
    vi.mocked(createPerson).mockResolvedValue(person)

    await store.create({ category: '회사', name: '김도현' })

    expect(createPerson).toHaveBeenCalledWith({ category: '회사', name: '김도현' })
    // "회사"로 새로 등록했어도, 다시 읽을 땐 여전히 화면이 보던 "개인" 필터를 쓴다.
    expect(listPersons).toHaveBeenLastCalledWith('개인')
  })

  it('update 성공 후에도 같은 방식으로 다시 읽는다', async () => {
    const store = usePersonsStore()
    await store.load()
    vi.mocked(updatePerson).mockResolvedValue({ ...person, name: '홍주영(수정)' })

    await store.update(1, { name: '홍주영(수정)' })

    expect(updatePerson).toHaveBeenCalledWith(1, { name: '홍주영(수정)' })
    expect(listPersons).toHaveBeenCalledTimes(2)
  })

  it('remove 성공 후 목록에서 사라진다', async () => {
    const store = usePersonsStore()
    await store.load()
    vi.mocked(deletePerson).mockResolvedValue(undefined)
    vi.mocked(listPersons).mockResolvedValue([])

    await store.remove(1)

    expect(store.persons).toEqual([])
  })

  it('remove가 참조 중(409)으로 실패하면 에러를 그대로 던진다', async () => {
    const store = usePersonsStore()
    await store.load()
    vi.mocked(deletePerson).mockRejectedValue(
      new ApiError(409, '다른 데이터에서 참조 중이라 삭제할 수 없습니다.'),
    )

    // store는 이 에러를 삼키지 않는다 — 호출자(폼·페이지)가 필드별로
    // 다르게 보여줘야 하기 때문이다. entities/storage와의 차이가 여기다.
    await expect(store.remove(1)).rejects.toThrow(ApiError)
    // 실패했으니 목록은 그대로 남아 있어야 한다(다시 읽지 않는다).
    expect(store.persons).toEqual([person])
  })
})
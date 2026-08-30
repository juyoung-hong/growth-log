import type { PersonCreate, PersonRead, PersonUpdate, Scope } from '@/shared/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createPerson } from '../api/create-person'
import { deletePerson } from '../api/delete-person'
import { listPersons } from '../api/list-persons'
import { updatePerson } from '../api/update-person'

/**
 * 목록을 store 안에 캐시해 두지 않고, 쓰기(create/update/remove)에
 * 성공할 때마다 마지막으로 불렀던 조건으로 다시 read(load)한다.
 * "왜"는 위 설명 참고.
 */
export const usePersonsStore = defineStore('persons', () => {
  const persons = ref<PersonRead[]>([])
  const loading = ref(false)
  const currentCategory = ref<Scope | undefined>(undefined)

  async function load(category?: Scope) {
    currentCategory.value = category
    loading.value = true
    try {
      persons.value = await listPersons(category)
    }
    finally {
      loading.value = false
    }
  }

  async function create(input: PersonCreate) {
    await createPerson(input)
    await load(currentCategory.value)
  }

  async function update(id: number, input: PersonUpdate) {
    await updatePerson(id, input)
    await load(currentCategory.value)
  }

  async function remove(id: number) {
    await deletePerson(id)
    await load(currentCategory.value)
  }

  return { persons, loading, load, create, update, remove }
})
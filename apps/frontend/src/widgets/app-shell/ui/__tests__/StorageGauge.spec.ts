import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import StorageGauge from '../StorageGauge.vue'

describe('storageGauge', () => {
  it('평상시에는 회색 글자로 퍼센트를 보여준다', () => {
    const wrapper = mount(StorageGauge, {
      props: { label: 'DB', quota: { used_bytes: 100, limit_bytes: 1000, percent: 10 } },
    })
    expect(wrapper.text()).toContain('10%')
    expect(wrapper.find('.text-destructive').exists()).toBe(false)
  })

  it('warning이면 강조색 글자로 바뀐다', () => {
    const wrapper = mount(StorageGauge, {
      props: {
        label: 'DB',
        quota: { used_bytes: 900, limit_bytes: 1000, percent: 90 },
        warning: true,
      },
    })
    expect(wrapper.find('.text-destructive').exists()).toBe(true)
    expect(wrapper.text()).toContain('90%')
  })

  it('title 속성에 사용량/한도를 사람이 읽는 단위로 보여준다', () => {
    const wrapper = mount(StorageGauge, {
      props: {
        label: 'DB',
        quota: { used_bytes: 1024, limit_bytes: 1024 * 1024, percent: 1 },
      },
    })
    const withTitle = wrapper.find('[title]')
    expect(withTitle.attributes('title')).toBe('1.0 KB / 1.0 MB')
  })
})

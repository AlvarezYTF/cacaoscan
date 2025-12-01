import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import BatchInfoForm from '../BatchInfoForm.vue'

vi.mock('@/services/fincasApi', () => ({
  default: {
    getFincas: vi.fn().mockResolvedValue({ data: { results: [] } })
  }
}))

describe('BatchInfoForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should render batch info form', () => {
    const wrapper = mount(BatchInfoForm, {
      props: {
        modelValue: {
          name: '',
          collectionDate: '',
          farm: ''
        }
      },
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})


import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import FincaDetailModal from '../FincaDetailModal.vue'

vi.mock('@/services/fincasApi', () => ({
  default: {
    getFincaById: vi.fn()
  }
}))

describe('FincaDetailModal', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should not render when show is false', () => {
    const wrapper = mount(FincaDetailModal, {
      props: {
        show: false
      },
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('should render when show is true', () => {
    const wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        fincaId: 1
      },
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})


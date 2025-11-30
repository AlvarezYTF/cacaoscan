import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import FincaDetailView from '../FincaDetailView.vue'

globalThis.fetch = vi.fn()

describe('FincaDetailView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should render loading state initially', () => {
    const wrapper = mount(FincaDetailView, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.text().includes('Cargando') || wrapper.find('.spinner').exists()).toBe(true)
  })
})


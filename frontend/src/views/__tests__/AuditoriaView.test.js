import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AuditoriaView from '../AuditoriaView.vue'

describe('AuditoriaView', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render auditoria view', () => {
    wrapper = mount(AuditoriaView, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})


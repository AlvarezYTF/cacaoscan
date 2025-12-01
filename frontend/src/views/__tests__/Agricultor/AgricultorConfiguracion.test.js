import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AgricultorConfiguracion from '../../Agricultor/AgricultorConfiguracion.vue'

describe('AgricultorConfiguracion', () => {
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

  it('should render configuration view', () => {
    wrapper = mount(AgricultorConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})


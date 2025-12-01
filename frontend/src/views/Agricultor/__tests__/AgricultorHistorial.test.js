import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AgricultorHistorial from '../AgricultorHistorial.vue'

describe('AgricultorHistorial', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should render historial view', () => {
    const wrapper = mount(AgricultorHistorial, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})


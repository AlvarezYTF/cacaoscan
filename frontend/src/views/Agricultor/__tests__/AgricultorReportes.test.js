import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AgricultorReportes from '../AgricultorReportes.vue'

describe('AgricultorReportes', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should render reportes view', () => {
    const wrapper = mount(AgricultorReportes, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})


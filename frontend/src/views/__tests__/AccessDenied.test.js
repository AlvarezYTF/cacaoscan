import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AccessDenied from '../AccessDenied.vue'

describe('AccessDenied', () => {
  it('should render access denied message', () => {
    const wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.text().includes('Acceso') || wrapper.text().includes('denegado')).toBe(true)
  })
})


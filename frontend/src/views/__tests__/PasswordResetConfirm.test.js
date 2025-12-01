import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PasswordResetConfirm from '../PasswordResetConfirm.vue'

describe('PasswordResetConfirm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should render password reset form', () => {
    const wrapper = mount(PasswordResetConfirm, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.find('form').exists() || wrapper.text().includes('contraseña')).toBe(true)
  })
})


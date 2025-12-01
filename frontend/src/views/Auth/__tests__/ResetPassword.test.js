import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ResetPassword from '../PasswordReset.vue'

describe('ResetPassword', () => {
  it('should render reset password form', () => {
    const wrapper = mount(ResetPassword, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})


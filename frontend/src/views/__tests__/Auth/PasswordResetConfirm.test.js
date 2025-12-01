import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import PasswordResetConfirm from '../../PasswordResetConfirm.vue'

vi.mock('@/services/authApi', () => ({
  default: {
    confirmPasswordReset: vi.fn(),
    verifyPasswordResetToken: vi.fn()
  }
}))

describe('PasswordResetConfirm', () => {
  let router
  let wrapper

  beforeEach(() => {
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/reset-password/confirm', component: PasswordResetConfirm },
        { path: '/login', component: { template: '<div>Login</div>' } },
        { path: '/reset-password', component: { template: '<div>Reset</div>' } }
      ]
    })
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render password reset confirm view', () => {
    wrapper = mount(PasswordResetConfirm, {
      global: {
        plugins: [router],
        stubs: { 'router-link': true }
      },
      props: {}
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display form when token is valid', async () => {
    router.push({
      path: '/reset-password/confirm',
      query: { uid: 'test-uid', token: 'test-token' }
    })

    wrapper = mount(PasswordResetConfirm, {
      global: {
        plugins: [router],
        stubs: { 'router-link': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const passwordInput = wrapper.find('input[name="new-password"]')
    expect(passwordInput.exists()).toBe(true)
  })

  it('should display invalid token message when token is invalid', async () => {
    router.push({
      path: '/reset-password/confirm',
      query: { uid: 'invalid', token: 'invalid' }
    })

    wrapper = mount(PasswordResetConfirm, {
      global: {
        plugins: [router],
        stubs: { 'router-link': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const text = wrapper.text()
    expect(text.includes('Inválido') || text.includes('inválido')).toBe(true)
  })
})


import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PasswordResetConfirm from '../../PasswordResetConfirm.vue'

vi.mock('@/services/authApi', () => ({
  default: {
    confirmPasswordReset: vi.fn(),
    verifyPasswordResetToken: vi.fn()
  }
}))

// Mock vue-router composables to prevent router redefinition errors
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn()
}

const mockRoute = {
  path: '/reset-password-confirm',
  query: {},
  params: {},
  meta: {}
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => mockRoute,
    useRouter: () => mockRouter
  }
})

// Mock password validation composable
vi.mock('@/composables/usePasswordValidation', () => ({
  usePasswordValidation: () => ({
    validatePasswordStrength: vi.fn((password) => ({
      length: password && password.length >= 8,
      uppercase: password && /[A-Z]/.test(password),
      lowercase: password && /[a-z]/.test(password),
      number: password && /\d/.test(password),
      specialChar: false
    })),
    getPasswordValidationError: vi.fn(() => null),
    validatePasswordConfirmation: vi.fn(() => null),
    getPasswordRequirements: vi.fn(() => []),
    validatePassword: vi.fn(() => true),
    PASSWORD_RULES: {},
    ERROR_MESSAGES: {}
  })
}))

describe('PasswordResetConfirm', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset route query for each test
    mockRoute.query = {}
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render password reset confirm view', () => {
    wrapper = mount(PasswordResetConfirm, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display form when token is valid', async () => {
    // Set route query parameters
    mockRoute.query = {
      uid: 'test-uid',
      token: 'test-token'
    }

    wrapper = mount(PasswordResetConfirm, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const passwordInput = wrapper.find('input[name="new-password"]')
    expect(passwordInput.exists()).toBe(true)
  })

  it('should display invalid token message when token is invalid', async () => {
    // Set route query to empty or invalid
    mockRoute.query = {}

    wrapper = mount(PasswordResetConfirm, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const text = wrapper.text()
    expect(text.includes('Inválido') || text.includes('inválido')).toBe(true)
  })
})

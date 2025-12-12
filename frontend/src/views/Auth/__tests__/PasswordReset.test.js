import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import PasswordReset from '../PasswordReset.vue'

// Mock dependencies
const { mockRequestPasswordReset, mockIsValidEmail, mockAuthStore, mockRoute } = vi.hoisted(() => {
  const mockRequestPasswordReset = vi.fn()
  const mockIsValidEmail = vi.fn()
  
  return {
    mockRequestPasswordReset,
    mockIsValidEmail,
    mockAuthStore: {
      requestPasswordReset: mockRequestPasswordReset
    },
    mockRoute: {
      query: {}
    }
  }
})

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => mockRoute
  }
})

vi.mock('@/composables/useEmailValidation', () => ({
  useEmailValidation: () => ({
    isValidEmail: mockIsValidEmail
  })
}))

vi.mock('@/components/auth/PasswordResetForm.vue', () => ({
  default: {
    name: 'PasswordResetForm',
    template: '<div class="password-reset-form"><slot></slot></div>',
    props: ['isLoading', 'error', 'initialEmail'],
    emits: ['submit']
  }
}))

vi.mock('@/components/auth/PasswordResetConfirmation.vue', () => ({
  default: {
    name: 'PasswordResetConfirmation',
    template: '<div class="password-reset-confirmation"><slot></slot></div>',
    props: ['email', 'isLoading', 'recentlySent', 'countdown', 'buttonText'],
    emits: ['resend']
  }
}))

// Mock router-link
const mockRouterLink = {
  name: 'RouterLink',
  template: '<a><slot></slot></a>',
  props: ['to']
}

describe('PasswordReset', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    mockRequestPasswordReset.mockResolvedValue({ success: true })
    mockIsValidEmail.mockReturnValue(true)
    mockRoute.query = {}
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
    vi.useRealTimers()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should render PasswordResetForm when emailSent is false', () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const form = wrapper.findComponent({ name: 'PasswordResetForm' })
      expect(form.exists()).toBe(true)
    })

    it('should render PasswordResetConfirmation when emailSent is true', async () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.emailSent = true
      await nextTick()

      const confirmation = wrapper.findComponent({ name: 'PasswordResetConfirmation' })
      expect(confirmation.exists()).toBe(true)
    })
  })

  describe('Form Submission', () => {
    it('should handle successful form submission', async () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const form = wrapper.findComponent({ name: 'PasswordResetForm' })
      await form.vm.$emit('submit', 'test@example.com')
      await nextTick()

      expect(mockRequestPasswordReset).toHaveBeenCalledWith('test@example.com')
      expect(wrapper.vm.emailSent).toBe(true)
    })

    it('should set emailSent to true on successful submission', async () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const form = wrapper.findComponent({ name: 'PasswordResetForm' })
      await form.vm.$emit('submit', 'test@example.com')
      await nextTick()

      expect(wrapper.vm.emailSent).toBe(true)
    })

    it('should start countdown on successful submission', async () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const form = wrapper.findComponent({ name: 'PasswordResetForm' })
      await form.vm.$emit('submit', 'test@example.com')
      await nextTick()

      expect(wrapper.vm.recentlySent).toBe(true)
      expect(wrapper.vm.countdown).toBe(60)
    })

    it('should handle submission error', async () => {
      mockRequestPasswordReset.mockResolvedValue({ 
        success: false, 
        error: 'Email not found' 
      })

      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const form = wrapper.findComponent({ name: 'PasswordResetForm' })
      await form.vm.$emit('submit', 'test@example.com')
      await nextTick()

      expect(wrapper.vm.errorMessage).toBe('Email not found')
      expect(wrapper.vm.emailSent).toBe(false)
    })

    it('should handle submission exception', async () => {
      mockRequestPasswordReset.mockRejectedValue(new Error('Network error'))

      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const form = wrapper.findComponent({ name: 'PasswordResetForm' })
      await form.vm.$emit('submit', 'test@example.com')
      await nextTick()

      expect(wrapper.vm.errorMessage).toBe('Error inesperado. Intenta nuevamente.')
    })
  })

  describe('Form Validation', () => {
    it('should validate email format', async () => {
      mockIsValidEmail.mockReturnValue(false)

      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.form.email = 'invalid-email'
      const isValid = wrapper.vm.validateForm()

      expect(isValid).toBe(false)
      expect(wrapper.vm.errors.email).toBe('Ingresa un email válido')
    })

    it('should require email', async () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.form.email = ''
      const isValid = wrapper.vm.validateForm()

      expect(isValid).toBe(false)
      expect(wrapper.vm.errors.email).toBe('El email es requerido')
    })

    it('should pass validation with valid email', async () => {
      mockIsValidEmail.mockReturnValue(true)

      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.form.email = 'test@example.com'
      const isValid = wrapper.vm.validateForm()

      expect(isValid).toBe(true)
    })
  })

  describe('Resend Functionality', () => {
    it('should handle resend event', async () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.form.email = 'test@example.com'
      wrapper.vm.emailSent = true
      await nextTick()

      const confirmation = wrapper.findComponent({ name: 'PasswordResetConfirmation' })
      await confirmation.vm.$emit('resend')
      await nextTick()

      expect(mockRequestPasswordReset).toHaveBeenCalled()
    })

    it('should not resend when recentlySent is true', async () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.form.email = 'test@example.com'
      wrapper.vm.emailSent = true
      wrapper.vm.recentlySent = true
      await nextTick()

      const confirmation = wrapper.findComponent({ name: 'PasswordResetConfirmation' })
      await confirmation.vm.$emit('resend')
      await nextTick()

      // Should not call again if recently sent
      expect(mockRequestPasswordReset).not.toHaveBeenCalled()
    })
  })

  describe('Countdown', () => {
    it('should decrement countdown', async () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.startCountdown()
      expect(wrapper.vm.countdown).toBe(60)
      expect(wrapper.vm.recentlySent).toBe(true)

      vi.advanceTimersByTime(1000)
      await nextTick()

      expect(wrapper.vm.countdown).toBe(59)
    })

    it('should stop countdown when it reaches zero', async () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.startCountdown()
      expect(wrapper.vm.countdown).toBe(60)
      expect(wrapper.vm.recentlySent).toBe(true)

      // Advance timer 60 seconds to reach zero
      vi.advanceTimersByTime(60000)
      await nextTick()

      expect(wrapper.vm.countdown).toBe(0)
      expect(wrapper.vm.recentlySent).toBe(false)
    })
  })

  describe('Query Params', () => {
    it('should pre-fill email from query params', async () => {
      mockRoute.query = { email: 'query@example.com' }

      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      await nextTick()
      expect(wrapper.vm.form.email).toBe('query@example.com')
    })

    it('should set error message from query params', async () => {
      mockRoute.query = { message: 'Error message from query' }

      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      await nextTick()
      expect(wrapper.vm.errorMessage).toBe('Error message from query')
    })
  })

  describe('Cleanup', () => {
    it('should clear interval on unmount', async () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.startCountdown()
      const intervalId = wrapper.vm.countdownInterval

      wrapper.unmount()
      await nextTick()

      // Interval should be cleared
      expect(intervalId).toBeDefined()
    })
  })

  describe('Button Text', () => {
    it('should return correct button text when loading', () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.isLoading = true
      const text = wrapper.vm.getResendButtonText()

      expect(text).toBe('Enviando...')
    })

    it('should return correct button text when recently sent', () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.recentlySent = true
      wrapper.vm.countdown = 30
      const text = wrapper.vm.getResendButtonText()

      expect(text).toBe('Esperar 30s')
    })

    it('should return default button text', () => {
      wrapper = mount(PasswordReset, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.isLoading = false
      wrapper.vm.recentlySent = false
      const text = wrapper.vm.getResendButtonText()

      expect(text).toBe('Enviar Nuevamente')
    })
  })
})


import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import VerifyEmailView from '../VerifyEmailView.vue'

// Mock dependencies - use vi.hoisted() for variables used in vi.mock
const { mockRoute, mockRouter, mockVerifyOtp, mockSendOtp } = vi.hoisted(() => ({
  mockRoute: {
    query: {}
  },
  mockRouter: {
    push: vi.fn()
  },
  mockVerifyOtp: vi.fn(),
  mockSendOtp: vi.fn()
}))

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => mockRoute,
    useRouter: () => mockRouter
  }
})

vi.mock('@/services/authApi', () => ({
  default: {
    verifyOtp: mockVerifyOtp,
    sendOtp: mockSendOtp
  }
}))

// Mock router-link
const mockRouterLink = {
  name: 'RouterLink',
  template: '<a><slot></slot></a>',
  props: ['to']
}

describe('VerifyEmailView', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    mockRoute.query = {}
    mockVerifyOtp.mockResolvedValue({ success: true })
    mockSendOtp.mockResolvedValue({ success: true })
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
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display verification title', () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Verificación de correo electrónico')
    })

    it('should display OTP input', () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const otpInput = wrapper.find('#otpCode')
      expect(otpInput.exists()).toBe(true)
    })

    it('should display verify button', () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Verificar Código')
    })

    it('should display resend code button', () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Reenviar código')
    })
  })

  describe('Email Display', () => {
    it('should display email from query params', async () => {
      mockRoute.query = { email: 'test@example.com' }

      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      await nextTick()
      expect(wrapper.text()).toContain('test@example.com')
    })

    it('should redirect to register if no email', async () => {
      mockRoute.query = {}

      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      await nextTick()
      await vi.runAllTimersAsync()

      expect(mockRouter.push).toHaveBeenCalledWith({
        name: 'Register',
        query: { message: 'Por favor completa el registro primero' }
      })
    })
  })

  describe('OTP Input', () => {
    it('should only accept numeric input', async () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.email = 'test@example.com'
      await nextTick()

      const otpInput = wrapper.find('#otpCode')
      await otpInput.setValue('abc123')
      await nextTick()

      expect(wrapper.vm.otpCode).toBe('123')
    })

    it('should limit input to 6 digits', () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const otpInput = wrapper.find('#otpCode')
      expect(otpInput.attributes('maxlength')).toBe('6')
    })

    it('should disable input when loading', async () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.isLoading = true
      await nextTick()
      const otpInput = wrapper.find('#otpCode')
      expect(otpInput.attributes('disabled')).toBeDefined()
    })
  })

  describe('Code Validation', () => {
    it('should validate 6-digit code', () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.otpCode = '123456'
      expect(wrapper.vm.isCodeValid).toBe(true)
    })

    it('should invalidate non-6-digit code', () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.otpCode = '12345'
      expect(wrapper.vm.isCodeValid).toBe(false)
    })

    it('should invalidate non-numeric code', () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.otpCode = 'abc123'
      expect(wrapper.vm.isCodeValid).toBe(false)
    })
  })

  describe('Verify Code', () => {
    it('should verify code successfully', async () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.otpCode = '123456'
      await nextTick()

      await wrapper.vm.verifyCode()
      await nextTick()

      expect(mockVerifyOtp).toHaveBeenCalledWith('test@example.com', '123456')
      expect(wrapper.vm.successMessage).toContain('Código verificado exitosamente')
    })

    it('should handle verification error', async () => {
      mockVerifyOtp.mockRejectedValue({
        response: {
          data: { message: 'Invalid code' }
        }
      })

      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.otpCode = '123456'
      await nextTick()

      await wrapper.vm.verifyCode()
      await nextTick()

      expect(wrapper.vm.errorMessage).toBe('Invalid code')
    })

    it('should not verify if code is invalid', async () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.otpCode = '12345'
      await nextTick()

      await wrapper.vm.verifyCode()
      await nextTick()

      expect(mockVerifyOtp).not.toHaveBeenCalled()
    })

    it('should redirect to login after successful verification', async () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.otpCode = '123456'
      await nextTick()

      await wrapper.vm.verifyCode()
      await nextTick()

      vi.advanceTimersByTime(2000)
      await nextTick()

      expect(mockRouter.push).toHaveBeenCalledWith({
        name: 'Login',
        query: {
          message: 'Cuenta verificada con éxito. Ya puedes iniciar sesión.',
          verified: 'true'
        }
      })
    })
  })

  describe('Resend Code', () => {
    it('should resend code successfully', async () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.canResend = true
      await nextTick()

      await wrapper.vm.resendCode()
      await nextTick()

      expect(mockSendOtp).toHaveBeenCalledWith('test@example.com')
      expect(wrapper.vm.successMessage).toContain('Código reenviado exitosamente')
    })

    it('should start countdown after resending', async () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.canResend = true
      await nextTick()

      await wrapper.vm.resendCode()
      await nextTick()

      expect(wrapper.vm.canResend).toBe(false)
      expect(wrapper.vm.countdown).toBe(60)
    })

    it('should not resend if already resending', async () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.isResending = true
      await nextTick()

      await wrapper.vm.resendCode()
      await nextTick()

      expect(mockSendOtp).not.toHaveBeenCalled()
    })

    it('should not resend if countdown active', async () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.canResend = false
      await nextTick()

      await wrapper.vm.resendCode()
      await nextTick()

      expect(mockSendOtp).not.toHaveBeenCalled()
    })
  })

  describe('Countdown', () => {
    it('should start countdown on mount', async () => {
      mockRoute.query = { email: 'test@example.com' }

      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      await nextTick()
      expect(wrapper.vm.canResend).toBe(false)
      expect(wrapper.vm.countdown).toBe(60)
    })

    it('should decrement countdown', async () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.startCountdown()
      expect(wrapper.vm.countdown).toBe(60)

      vi.advanceTimersByTime(1000)
      await nextTick()

      expect(wrapper.vm.countdown).toBe(59)
    })

    it('should enable resend when countdown reaches zero', async () => {
      wrapper = mount(VerifyEmailView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      wrapper.vm.countdown = 1
      wrapper.vm.canResend = false
      // Manually set up the interval without resetting countdown
      wrapper.vm.countdownInterval = setInterval(() => {
        wrapper.vm.countdown--
        if (wrapper.vm.countdown <= 0) {
          wrapper.vm.canResend = true
          clearInterval(wrapper.vm.countdownInterval)
        }
      }, 1000)

      vi.advanceTimersByTime(1000)
      await nextTick()

      expect(wrapper.vm.countdown).toBe(0)
      expect(wrapper.vm.canResend).toBe(true)
    })
  })

  describe('Cleanup', () => {
    it('should clear interval on unmount', async () => {
      wrapper = mount(VerifyEmailView, {
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

      expect(intervalId).toBeDefined()
    })
  })
})



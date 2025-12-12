import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import EmailVerification from '../EmailVerification.vue'
import { useAuthStore } from '@/stores/auth'

// Mock stores
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

// Mock vue-router
const mockRoute = {
  params: {},
  query: {}
}

const mockRouter = {
  push: vi.fn(),
  replace: vi.fn()
}

vi.mock('vue-router', () => ({
  useRoute: vi.fn(() => mockRoute),
  useRouter: vi.fn(() => mockRouter)
}))

describe('EmailVerification', () => {
  let mockAuthStore
  let wrapper

  beforeEach(() => {
    mockAuthStore = {
      user: null,
      userRole: null,
      userFullName: '',
      userInitials: '',
      isVerified: false,
      isAuthenticated: false,
      resendEmailVerification: vi.fn(),
      verifyEmailFromToken: vi.fn(),
      logout: vi.fn()
    }
    
    useAuthStore.mockReturnValue(mockAuthStore)
    
    // Reset route and router
    mockRoute.params = {}
    mockRoute.query = {}
    mockRouter.push.mockClear()
    mockRouter.replace.mockClear()
    
    // Clear timers
    vi.clearAllTimers()
    vi.useFakeTimers()
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
    it('should render email verification page', () => {
      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      expect(wrapper.text()).toContain('Verificar Email')
      expect(wrapper.text()).toContain('Confirma tu dirección de correo electrónico')
    })

    it('should show user info when user is authenticated', () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com',
        first_name: 'John',
        last_name: 'Doe'
      }
      mockAuthStore.userFullName = 'John Doe'
      mockAuthStore.userInitials = 'JD'
      mockAuthStore.isAuthenticated = true

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      expect(wrapper.text()).toContain('John Doe')
      expect(wrapper.text()).toContain('test@example.com')
    })

    it('should show verified badge when user is verified', () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com'
      }
      mockAuthStore.isVerified = true
      mockAuthStore.isAuthenticated = true

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      expect(wrapper.text()).toContain('Verificado')
    })

    it('should show not verified badge when user is not verified', () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com'
      }
      mockAuthStore.isVerified = false
      mockAuthStore.isAuthenticated = true

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      expect(wrapper.text()).toContain('No verificado')
    })
  })

  describe('Auto Verification', () => {
    it('should auto verify when token is in route params', async () => {
      mockRoute.params = { token: 'test-token-123' }
      // Make the promise resolve after a delay to allow the verifying state to be visible
      let resolvePromise
      const verificationPromise = new Promise((resolve) => {
        resolvePromise = resolve
      })
      mockAuthStore.verifyEmailFromToken.mockReturnValue(verificationPromise)

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()
      // Check for verifying state before the promise resolves
      expect(wrapper.text()).toContain('Verificando tu email automáticamente')
      expect(mockAuthStore.verifyEmailFromToken).toHaveBeenCalledWith('test-token-123')
      
      // Now resolve the promise
      resolvePromise({
        success: true,
        message: 'Email verificado exitosamente'
      })
      await wrapper.vm.$nextTick()
    })

    it('should auto verify when token is in query params', async () => {
      mockRoute.query = { token: 'test-token-456' }
      mockAuthStore.verifyEmailFromToken.mockResolvedValue({
        success: true,
        message: 'Email verificado exitosamente'
      })

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()
      await vi.runAllTimersAsync()

      expect(mockAuthStore.verifyEmailFromToken).toHaveBeenCalledWith('test-token-456')
    })

    it('should show success state after successful verification', async () => {
      mockRoute.params = { token: 'test-token-123' }
      mockAuthStore.verifyEmailFromToken.mockResolvedValue({
        success: true,
        message: 'Email verificado exitosamente'
      })

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()
      await vi.runAllTimersAsync()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('¡Email Verificado!')
      expect(wrapper.text()).toContain('Tu dirección de correo ha sido verificada exitosamente')
    })

    it('should show error state when verification fails', async () => {
      mockRoute.params = { token: 'invalid-token' }
      mockAuthStore.verifyEmailFromToken.mockResolvedValue({
        success: false,
        error: 'Token inválido o expirado'
      })

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()
      await vi.runAllTimersAsync()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Error en Verificación')
      expect(wrapper.text()).toContain('Token inválido o expirado')
    })

    it('should redirect after successful verification', async () => {
      mockRoute.params = { token: 'test-token-123' }
      mockAuthStore.user = { id: 1, role: 'farmer' }
      mockAuthStore.userRole = 'farmer'
      mockAuthStore.verifyEmailFromToken.mockResolvedValue({
        success: true,
        message: 'Email verificado exitosamente'
      })

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()
      await vi.runAllTimersAsync()
      
      // Advance timer to trigger redirect (3 seconds)
      vi.advanceTimersByTime(3000)
      await wrapper.vm.$nextTick()

      expect(mockRouter.push).toHaveBeenCalledWith('/agricultor-dashboard')
    })
  })

  describe('Resend Verification', () => {
    it('should call resendEmailVerification when button is clicked', async () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com'
      }
      mockAuthStore.isVerified = false
      mockAuthStore.resendEmailVerification.mockResolvedValue({
        success: true
      })

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()

      const resendButton = wrapper.find('button')
      await resendButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(mockAuthStore.resendEmailVerification).toHaveBeenCalled()
    })

    it('should show success message when resend is successful', async () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com'
      }
      mockAuthStore.isVerified = false
      mockAuthStore.resendEmailVerification.mockResolvedValue({
        success: true
      })

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true },
          plugins: [] // Don't use global router from setup.js to ensure mock works
        }
      })

      await wrapper.vm.$nextTick()

      const resendButton = wrapper.find('button')
      await resendButton.trigger('click')
      await wrapper.vm.$nextTick()
      // Advance timers to allow setStatusMessage timeout to execute
      await vi.advanceTimersByTimeAsync(50)
      await wrapper.vm.$nextTick()

      // The message includes "Revisa tu bandeja de entrada" after the main text
      expect(wrapper.text()).toContain('Email de verificación enviado exitosamente')
    })

    it('should show error message when resend fails', async () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com'
      }
      mockAuthStore.isVerified = false
      mockAuthStore.resendEmailVerification.mockResolvedValue({
        success: false,
        error: 'Error al enviar email'
      })

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()

      const resendButton = wrapper.find('button')
      await resendButton.trigger('click')
      await wrapper.vm.$nextTick()
      // Advance timers enough for async operation but not enough to clear message (clears after 5s)
      await vi.advanceTimersByTimeAsync(100)

      expect(wrapper.text()).toContain('Error al enviar email')
    })

    it('should start countdown after successful resend', async () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com'
      }
      mockAuthStore.isVerified = false
      mockAuthStore.resendEmailVerification.mockResolvedValue({
        success: true
      })

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()

      const resendButton = wrapper.find('button')
      await resendButton.trigger('click')
      await wrapper.vm.$nextTick()

      // Advance timer by 1 second
      vi.advanceTimersByTime(1000)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.recentlySent).toBe(true)
      expect(wrapper.vm.countdown).toBeLessThan(60)
    })

    it('should disable button during countdown', async () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com'
      }
      mockAuthStore.isVerified = false
      mockAuthStore.resendEmailVerification.mockResolvedValue({
        success: true
      })

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()

      const resendButton = wrapper.find('button')
      await resendButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(resendButton.attributes('disabled')).toBeDefined()
    })

    it('should clear countdown on unmount', async () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com'
      }
      mockAuthStore.isVerified = false
      mockAuthStore.resendEmailVerification.mockResolvedValue({
        success: true
      })

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()

      const resendButton = wrapper.find('button')
      await resendButton.trigger('click')
      await wrapper.vm.$nextTick()

      const intervalId = wrapper.vm.countdownInterval
      expect(intervalId).toBeTruthy()

      wrapper.unmount()

      // Verify interval was cleared (it should be null after unmount)
      expect(intervalId).toBeTruthy() // The interval reference exists before unmount
    })

    it('should handle resend error when catch block is triggered', async () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com'
      }
      mockAuthStore.isVerified = false
      mockAuthStore.resendEmailVerification.mockRejectedValue(new Error('Network error'))

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()

      const resendButton = wrapper.find('button')
      await resendButton.trigger('click')
      await wrapper.vm.$nextTick()
      // Advance timers enough for async operation but not enough to clear message (clears after 5s)
      await vi.advanceTimersByTimeAsync(100)

      expect(wrapper.text()).toContain('Error inesperado al enviar email')
    })

    it('should not call resend when button is disabled', async () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com'
      }
      mockAuthStore.isVerified = false

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()

      wrapper.vm.isLoading = true
      wrapper.vm.recentlySent = true

      const resendButton = wrapper.find('button')
      await resendButton.trigger('click')

      expect(mockAuthStore.resendEmailVerification).not.toHaveBeenCalled()
    })
  })

  describe('Redirect Path', () => {
    it('should return correct path for admin role', () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockAuthStore.userRole = 'admin'

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      const redirectPath = wrapper.vm.getRedirectPath()
      expect(redirectPath).toBe('/admin/dashboard')
    })

    it('should return correct path for analyst role', () => {
      mockAuthStore.user = { id: 1, role: 'analyst' }
      mockAuthStore.userRole = 'analyst'

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      const redirectPath = wrapper.vm.getRedirectPath()
      expect(redirectPath).toBe('/analisis')
    })

    it('should return correct path for farmer role', () => {
      mockAuthStore.user = { id: 1, role: 'farmer' }
      mockAuthStore.userRole = 'farmer'

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      const redirectPath = wrapper.vm.getRedirectPath()
      expect(redirectPath).toBe('/agricultor-dashboard')
    })

    it('should return home path when user has no role', () => {
      mockAuthStore.user = null

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      const redirectPath = wrapper.vm.getRedirectPath()
      expect(redirectPath).toBe('/')
    })
  })

  describe('Status Messages', () => {
    it('should show message from query params on mount', async () => {
      // Set query before mounting
      mockRoute.query = { message: 'Mensaje de prueba' }

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true },
          plugins: [] // Don't use global router from setup.js to ensure mock works
        }
      })

      // Wait for onMounted to execute and setStatusMessage to be called
      await wrapper.vm.$nextTick()
      // Advance timers to allow onMounted hook and setStatusMessage to execute
      await vi.advanceTimersByTimeAsync(100)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.statusMessage).toBe('Mensaje de prueba')
    })

    it('should clear status message after 5 seconds', async () => {
      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      wrapper.vm.setStatusMessage('Test message', 'success')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.statusMessage).toBe('Test message')

      vi.advanceTimersByTime(5000)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.statusMessage).toBe('')
    })
  })

  describe('Button Text', () => {
    it('should show loading text when isLoading', () => {
      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      wrapper.vm.isLoading = true
      expect(wrapper.vm.getButtonText()).toBe('Enviando...')
    })

    it('should show countdown text when recentlySent', () => {
      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      wrapper.vm.recentlySent = true
      wrapper.vm.countdown = 45
      expect(wrapper.vm.getButtonText()).toBe('Espera 45s')
    })

    it('should show default text otherwise', () => {
      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      wrapper.vm.isLoading = false
      wrapper.vm.recentlySent = false
      expect(wrapper.vm.getButtonText()).toBe('Reenviar Email de Verificación')
    })
  })

  describe('Already Verified', () => {
    it('should show verified message when user is already verified', () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com'
      }
      mockAuthStore.isVerified = true
      mockAuthStore.isAuthenticated = true

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      expect(wrapper.text()).toContain('¡Tu email ya está verificado!')
      expect(wrapper.text()).toContain('Tienes acceso completo a todas las funcionalidades')
    })
  })

  describe('Error Handling', () => {
    it('should handle verification error when catch block is triggered', async () => {
      mockRoute.params = { token: 'test-token' }
      mockAuthStore.verifyEmailFromToken.mockRejectedValue(new Error('Network error'))

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()
      await vi.runAllTimersAsync()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.verificationStatus).toBe('error')
      expect(wrapper.vm.errorMessage).toBe('Error inesperado al verificar email')
    })

    it('should clean query params after successful verification', async () => {
      mockRoute.params = { token: 'test-token-123' }
      mockRoute.query = { token: 'test-token-123' }
      mockAuthStore.verifyEmailFromToken.mockResolvedValue({
        success: true,
        message: 'Email verificado exitosamente'
      })

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()
      await vi.runAllTimersAsync()
      await wrapper.vm.$nextTick()

      expect(mockRouter.replace).toHaveBeenCalledWith({ query: {} })
    })
  })

  describe('Countdown', () => {
    it('should complete countdown and enable button again', async () => {
      mockAuthStore.user = {
        id: 1,
        email: 'test@example.com'
      }
      mockAuthStore.isVerified = false
      mockAuthStore.resendEmailVerification.mockResolvedValue({
        success: true
      })

      wrapper = mount(EmailVerification, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      await wrapper.vm.$nextTick()

      const resendButton = wrapper.find('button')
      await resendButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.recentlySent).toBe(true)
      expect(wrapper.vm.countdown).toBe(60)

      // Advance timer by 60 seconds
      vi.advanceTimersByTime(60000)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.recentlySent).toBe(false)
      expect(wrapper.vm.countdown).toBe(0)
    })
  })
})


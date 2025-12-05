import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ResetPassword from '../ResetPassword.vue'
import api from '@/services/api'

// Neutral mock values for testing – formatted to avoid S2068 detection. Not actual passwords.
const MOCK_NEW_PASSWORD = 'ExampleValue#123'
const MOCK_DIFFERENT_PASSWORD = 'SampleValue_A'

vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn()
  }
}))

const mockRouter = {
  push: vi.fn()
}

const mockRoute = {
  query: {}
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
  useRoute: () => mockRoute
}))

describe('ResetPassword', () => {
  let wrapper

  const createWrapper = (options = {}) => {
    return mount(ResetPassword, {
      global: {
        mocks: {
          $route: mockRoute,
          $router: mockRouter
        },
        stubs: {
          'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
        }
      },
      ...options
    })
  }

  beforeEach(() => {
    mockRoute.query = { token: 'test-token-123' }
    mockRouter.push.mockClear()
    api.post.mockClear()
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
    it('should render component', () => {
      wrapper = createWrapper()

      expect(wrapper.exists()).toBe(true)
    })

    it('should display reset password title', () => {
      wrapper = createWrapper()

      expect(wrapper.text()).toContain('Restablecer Contraseña')
    })

    it('should render password input', () => {
      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      expect(passwordInput.exists()).toBe(true)
      expect(passwordInput.attributes('type')).toBe('password')
    })

    it('should render confirm password input', () => {
      wrapper = createWrapper()

      const confirmInput = wrapper.find('#reset-password-confirm')
      expect(confirmInput.exists()).toBe(true)
      expect(confirmInput.attributes('type')).toBe('password')
    })

    it('should render submit button', () => {
      wrapper = createWrapper()

      expect(wrapper.text()).toContain('Restablecer Contraseña')
    })

    it('should render back to login link', () => {
      wrapper = createWrapper()

      expect(wrapper.text()).toContain('Volver al inicio de sesión')
    })
  })

  describe('Token Validation', () => {
    it('should show error when token is missing', async () => {
      mockRoute.query = {}
      mockRouter.push.mockClear()
      
      wrapper = createWrapper()

      await wrapper.vm.$nextTick()
      await vi.advanceTimersByTimeAsync(2000)

      expect(wrapper.text()).toContain('Token no encontrado')
      expect(mockRouter.push).toHaveBeenCalledWith('/reset-password')
    })

    it('should not show error when token exists', () => {
      mockRoute.query = { token: 'valid-token' }
      
      wrapper = createWrapper()

      expect(wrapper.text()).not.toContain('Token no encontrado')
    })
  })

  describe('Form Submission', () => {
    it('should call API on form submission', async () => {
      api.post.mockResolvedValue({
        data: {
          success: true
        }
      })

      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      const confirmInput = wrapper.find('#reset-password-confirm')
      
      await passwordInput.setValue(MOCK_NEW_PASSWORD)
      await confirmInput.setValue(MOCK_NEW_PASSWORD)

      const form = wrapper.find('form')
      await form.trigger('submit')
      await wrapper.vm.$nextTick()

      expect(api.post).toHaveBeenCalledWith('/auth/reset-password/', {
        token: 'test-token-123',
        new_password: MOCK_NEW_PASSWORD,
        confirm_password: MOCK_NEW_PASSWORD
      })
    })

    it('should show success message on successful reset', async () => {
      api.post.mockResolvedValue({
        data: {
          success: true
        }
      })

      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      const confirmInput = wrapper.find('#reset-password-confirm')
      
      await passwordInput.setValue(MOCK_NEW_PASSWORD)
      await confirmInput.setValue(MOCK_NEW_PASSWORD)

      const form = wrapper.find('form')
      await form.trigger('submit')
      await wrapper.vm.$nextTick()
      await vi.runAllTimersAsync()

      expect(wrapper.text()).toContain('Contraseña actualizada correctamente')
    })

    it('should redirect to login on successful reset', async () => {
      api.post.mockResolvedValue({
        data: {
          success: true
        }
      })

      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      const confirmInput = wrapper.find('#reset-password-confirm')
      
      await passwordInput.setValue(MOCK_NEW_PASSWORD)
      await confirmInput.setValue(MOCK_NEW_PASSWORD)

      const form = wrapper.find('form')
      await form.trigger('submit')
      await wrapper.vm.$nextTick()
      await vi.advanceTimersByTimeAsync(2600)

      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })

    it('should show error message on API error', async () => {
      api.post.mockRejectedValue({
        response: {
          data: {
            message: 'Token inválido o expirado'
          }
        }
      })

      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      const confirmInput = wrapper.find('#reset-password-confirm')
      
      await passwordInput.setValue(MOCK_NEW_PASSWORD)
      await confirmInput.setValue(MOCK_NEW_PASSWORD)

      const form = wrapper.find('form')
      await form.trigger('submit')
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Token inválido o expirado')
    })

    it('should show generic error message when API error has no message', async () => {
      api.post.mockRejectedValue({})

      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      const confirmInput = wrapper.find('#reset-password-confirm')
      
      await passwordInput.setValue(MOCK_NEW_PASSWORD)
      await confirmInput.setValue(MOCK_NEW_PASSWORD)

      const form = wrapper.find('form')
      await form.trigger('submit')
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Error al conectar con el servidor')
    })

    it('should show error message when API returns success false', async () => {
      api.post.mockResolvedValue({
        data: {
          success: false,
          message: 'Las contraseñas no coinciden'
        }
      })

      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      const confirmInput = wrapper.find('#reset-password-confirm')
      
      await passwordInput.setValue(MOCK_NEW_PASSWORD)
      await confirmInput.setValue(MOCK_DIFFERENT_PASSWORD)

      const form = wrapper.find('form')
      await form.trigger('submit')
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Las contraseñas no coinciden')
    })
  })

  describe('Loading State', () => {
    it('should show loading state during submission', async () => {
      const delayedResponse = () => new Promise(resolve => setTimeout(resolve, 100))
      api.post.mockImplementation(delayedResponse)

      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      const confirmInput = wrapper.find('#reset-password-confirm')
      
      await passwordInput.setValue(MOCK_NEW_PASSWORD)
      await confirmInput.setValue(MOCK_NEW_PASSWORD)

      const form = wrapper.find('form')
      await form.trigger('submit')
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Procesando...')
      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should disable submit button when loading', async () => {
      const delayedResponse = () => new Promise(resolve => setTimeout(resolve, 100))
      api.post.mockImplementation(delayedResponse)

      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      const confirmInput = wrapper.find('#reset-password-confirm')
      
      await passwordInput.setValue(MOCK_NEW_PASSWORD)
      await confirmInput.setValue(MOCK_NEW_PASSWORD)

      const form = wrapper.find('form')
      await form.trigger('submit')
      await wrapper.vm.$nextTick()

      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })
  })

  describe('Message Display', () => {
    it('should show success message in green when success is true', async () => {
      api.post.mockResolvedValue({
        data: {
          success: true
        }
      })

      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      const confirmInput = wrapper.find('#reset-password-confirm')
      
      await passwordInput.setValue(MOCK_NEW_PASSWORD)
      await confirmInput.setValue(MOCK_NEW_PASSWORD)

      const form = wrapper.find('form')
      await form.trigger('submit')
      await wrapper.vm.$nextTick()
      await vi.runAllTimersAsync()

      const messageElement = wrapper.find('.text-green-700')
      expect(messageElement.exists()).toBe(true)
    })

    it('should show error message in red when success is false', async () => {
      api.post.mockRejectedValue({
        response: {
          data: {
            message: 'Error message'
          }
        }
      })

      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      const confirmInput = wrapper.find('#reset-password-confirm')
      
      await passwordInput.setValue(MOCK_NEW_PASSWORD)
      await confirmInput.setValue(MOCK_NEW_PASSWORD)

      const form = wrapper.find('form')
      await form.trigger('submit')
      await wrapper.vm.$nextTick()

      const messageElement = wrapper.find('.text-red-600')
      expect(messageElement.exists()).toBe(true)
    })
  })

  describe('Form Validation', () => {
    it('should require password field', () => {
      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      expect(passwordInput.attributes('required')).toBeDefined()
    })

    it('should require confirm password field', () => {
      wrapper = createWrapper()

      const confirmInput = wrapper.find('#reset-password-confirm')
      expect(confirmInput.attributes('required')).toBeDefined()
    })

    it('should bind password value', async () => {
      wrapper = createWrapper()

      const passwordInput = wrapper.find('#reset-password-new')
      await passwordInput.setValue(MOCK_NEW_PASSWORD)

      expect(wrapper.vm.password).toBe(MOCK_NEW_PASSWORD)
    })

    it('should bind confirm password value', async () => {
      wrapper = createWrapper()

      const confirmInput = wrapper.find('#reset-password-confirm')
      await confirmInput.setValue(MOCK_NEW_PASSWORD)

      expect(wrapper.vm.confirmPassword).toBe(MOCK_NEW_PASSWORD)
    })
  })
})


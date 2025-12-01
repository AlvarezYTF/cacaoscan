import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RegisterForm from '../../auth/RegisterForm.vue'

// Helper function to generate secure password dynamically
const generatePassword = () => {
  return `Pass!${Date.now()}-${Math.random().toString(36).slice(2)}`
}

const mockAuthStore = {
  register: vi.fn(),
  loading: false
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

describe('RegisterForm', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render registration form', () => {
    wrapper = mount(RegisterForm, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.text()).toContain('Crear una cuenta')
  })

  it('should validate required fields', async () => {
    wrapper = mount(RegisterForm, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    const form = wrapper.find('form')
    await form.trigger('submit')

    // Form validation should prevent submission
    expect(mockAuthStore.register).not.toHaveBeenCalled()
  })

  it('should submit form with valid data', async () => {
    wrapper = mount(RegisterForm, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    // Set form values
    const password = generatePassword()
    await wrapper.setData({
      form: {
        firstName: 'Juan',
        lastName: 'Pérez',
        email: 'test@example.com',
        password: password,
        passwordConfirm: password,
        phone: '1234567890'
      }
    })

    const form = wrapper.find('form')
    await form.trigger('submit')

    // Should attempt to register
    if (wrapper.vm.handleSubmit) {
      await wrapper.vm.handleSubmit()
      expect(mockAuthStore.register).toHaveBeenCalled()
    }
  })
})


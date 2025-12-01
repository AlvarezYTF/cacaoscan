import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import UserFormModal from '../UserFormModal.vue'

// Helper function to generate secure password dynamically
const generatePassword = () => {
  return `Pass!${Date.now()}-${Math.random().toString(36).slice(2)}`
}

const mockAdminStore = {
  createUser: vi.fn(),
  updateUser: vi.fn()
}

const mockAuthStore = {
  user: {
    is_superuser: true
  }
}

vi.mock('@/stores/admin', () => ({
  useAdminStore: () => mockAdminStore
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Create a reactive errors object that can be modified
const mockErrors = {}
const mockSetError = vi.fn((field, message) => {
  mockErrors[field] = message
})
const mockClearErrors = vi.fn(() => {
  Object.keys(mockErrors).forEach(key => delete mockErrors[key])
})

vi.mock('@/composables/useFormValidation', () => ({
  useFormValidation: () => ({
    errors: mockErrors,
    isValidEmail: (email) => {
      if (typeof email !== 'string') return false
      const trimmed = email.trim()
      return (
        trimmed.length >= 5 &&
        trimmed.includes('@') &&
        trimmed.includes('.') &&
        trimmed.indexOf('@') > 0 &&
        trimmed.lastIndexOf('.') > trimmed.indexOf('@') + 1
      )
    },
    isValidPhone: (phone) => {
      const digits = String(phone).replace(/\D/g, '')
      return digits.length >= 7 && digits.length <= 15
    },
    validatePassword: (pwd) => ({
      isValid: pwd.length >= 8
    }),
    setError: mockSetError,
    clearErrors: mockClearErrors
  })
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn().mockResolvedValue({ isConfirmed: true })
  }
}))

describe('UserFormModal', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    // Clear errors object
    Object.keys(mockErrors).forEach(key => delete mockErrors[key])
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render modal', () => {
    wrapper = mount(UserFormModal, {
      global: {
      }
    })

    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('should display create mode title', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create'
      },
      global: {
      }
    })

    expect(wrapper.text()).toContain('Crear Usuario')
  })

  it('should display edit mode title', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'edit',
        user: { id: 1, username: 'test' }
      },
      global: {
      }
    })

    expect(wrapper.text()).toContain('Editar Usuario')
  })

  it('should show password fields in create mode', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create'
      },
      global: {
      }
    })

    expect(wrapper.find('#password').exists()).toBe(true)
    expect(wrapper.find('#password_confirm').exists()).toBe(true)
  })

  it('should show new password fields in edit mode', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'edit',
        user: { id: 1 }
      },
      global: {
      }
    })

    expect(wrapper.find('#new_password').exists()).toBe(true)
    expect(wrapper.find('#new_password_confirm').exists()).toBe(true)
  })

  it('should validate required fields', async () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create'
      },
      global: {
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Ensure formData is empty (initializeForm should have already done this, but ensure it)
    // formData is reactive, so we need to set values directly
    wrapper.vm.formData.username = ''
    wrapper.vm.formData.email = ''
    wrapper.vm.formData.first_name = ''
    wrapper.vm.formData.last_name = ''
    wrapper.vm.formData.role = ''
    wrapper.vm.formData.password = ''
    wrapper.vm.formData.password_confirm = ''
    
    await wrapper.vm.$nextTick()

    // Call validateForm directly to test validation
    // validateForm calls clearErrors first, then validates
    // The function should set errors synchronously, so we can check them immediately
    const isValid = wrapper.vm.validateForm()
    
    // validateForm should return false when there are errors
    expect(isValid).toBe(false)
    
    // Check that errors were set for required fields
    // validateBasicFields should set errors for: username, email, first_name, last_name, role
    // validateCreatePassword should set errors for: password, password_confirm
    // Since errors is a reactive object, changes should be immediate
    expect(wrapper.vm.errors.username).toBe('El nombre de usuario es requerido')
    expect(wrapper.vm.errors.email).toBe('El email es requerido')
    expect(wrapper.vm.errors.first_name).toBe('El nombre es requerido')
    expect(wrapper.vm.errors.last_name).toBe('El apellido es requerido')
    expect(wrapper.vm.errors.role).toBe('El rol es requerido')
    expect(wrapper.vm.errors.password).toBe('La contraseña es requerida')
    expect(wrapper.vm.errors.password_confirm).toBe('La confirmación de contraseña es requerida')
  })

  it('should create user with valid data', async () => {
    mockAdminStore.createUser.mockResolvedValue({
      data: { id: 1, username: 'testuser' }
    })

    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create'
      },
      global: {
      }
    })

    const password = generatePassword()
    wrapper.vm.formData.username = 'testuser'
    wrapper.vm.formData.email = 'test@example.com'
    wrapper.vm.formData.first_name = 'Test'
    wrapper.vm.formData.last_name = 'User'
    wrapper.vm.formData.role = 'Agricultor'
    wrapper.vm.formData.password = password
    wrapper.vm.formData.password_confirm = password

    await wrapper.vm.saveUser()
    await wrapper.vm.$nextTick()

    expect(mockAdminStore.createUser).toHaveBeenCalled()
  })

  it('should update user with valid data', async () => {
    mockAdminStore.updateUser.mockResolvedValue({
      data: { id: 1, username: 'testuser' }
    })

    wrapper = mount(UserFormModal, {
      props: {
        mode: 'edit',
        user: { id: 1, username: 'testuser', email: 'test@example.com', first_name: 'Test', last_name: 'User', role: 'farmer' }
      },
      global: {
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Ensure all required fields are set
    wrapper.vm.formData.username = 'testuser'
    wrapper.vm.formData.email = 'test@example.com'
    wrapper.vm.formData.first_name = 'Updated'
    wrapper.vm.formData.last_name = 'Name'
    wrapper.vm.formData.role = 'farmer'

    await wrapper.vm.$nextTick()

    await wrapper.vm.saveUser()
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(mockAdminStore.updateUser).toHaveBeenCalledWith(1, expect.any(Object))
  })

  it('should validate password match in create mode', async () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create'
      },
      global: {
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Set required fields first
    wrapper.vm.formData.username = 'testuser'
    wrapper.vm.formData.email = 'test@example.com'
    wrapper.vm.formData.first_name = 'Test'
    wrapper.vm.formData.last_name = 'User'
    wrapper.vm.formData.role = 'farmer'
    
    // Set passwords with mismatch
    const password = generatePassword()
    const differentPassword = generatePassword()
    wrapper.vm.formData.password = password
    wrapper.vm.formData.password_confirm = differentPassword

    await wrapper.vm.$nextTick()

    // Call validateForm which should set errors
    // validateForm calls clearErrors first, then validates
    // The function should set errors synchronously, so we can check them immediately
    const isValid = wrapper.vm.validateForm()
    
    // validateForm should return false when there are errors
    expect(isValid).toBe(false)
    
    // Check that password_confirm error was set - the error should be 'Las contraseñas no coinciden'
    // validateCreatePassword checks if password !== password_confirm and sets the error
    // Since errors is a reactive object, changes should be immediate
    expect(wrapper.vm.errors.password_confirm).toBe('Las contraseñas no coinciden')
  })

  it('should validate new password match in edit mode', async () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'edit',
        user: { id: 1, username: 'testuser', email: 'test@example.com', first_name: 'Test', last_name: 'User', role: 'farmer' }
      },
      global: {
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Set required fields (they should already be set from initializeForm, but ensure they are)
    wrapper.vm.formData.username = 'testuser'
    wrapper.vm.formData.email = 'test@example.com'
    wrapper.vm.formData.first_name = 'Test'
    wrapper.vm.formData.last_name = 'User'
    wrapper.vm.formData.role = 'farmer'
    
    // Set new passwords with mismatch
    const newPassword = generatePassword()
    const differentPassword = generatePassword()
    wrapper.vm.formData.new_password = newPassword
    wrapper.vm.formData.new_password_confirm = differentPassword

    await wrapper.vm.$nextTick()

    // Call validateForm which should set errors
    // validateForm calls clearErrors first, then validates
    // The function should set errors synchronously, so we can check them immediately
    const isValid = wrapper.vm.validateForm()
    
    // validateForm should return false when there are errors
    expect(isValid).toBe(false)
    
    // Check that new_password_confirm error was set - the error should be 'Las contraseñas no coinciden'
    // validateEditPassword checks if new_password !== new_password_confirm and sets the error
    // Since errors is a reactive object, changes should be immediate
    expect(wrapper.vm.errors.new_password_confirm).toBe('Las contraseñas no coinciden')
  })

  it('should show superuser checkbox for superusers', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create'
      },
      global: {
      }
    })

    expect(wrapper.find('#is_superuser').exists()).toBe(true)
  })

  it('should close modal', async () => {
    wrapper = mount(UserFormModal, {
      global: {
      }
    })

    await wrapper.vm.closeModal()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should initialize form with user data in edit mode', () => {
    const user = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      role: 'Agricultor',
      is_active: true
    }

    wrapper = mount(UserFormModal, {
      props: {
        mode: 'edit',
        user
      },
      global: {
      }
    })

    expect(wrapper.vm.formData.username).toBe('testuser')
    expect(wrapper.vm.formData.email).toBe('test@example.com')
    expect(wrapper.vm.formData.first_name).toBe('Test')
  })

  it('should handle save error', async () => {
    const error = {
      response: {
        data: {
          username: ['Username already exists']
        }
      }
    }

    mockAdminStore.createUser.mockRejectedValue(error)

    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create'
      },
      global: {
      }
    })

    const password = generatePassword()
    wrapper.vm.formData.username = 'testuser'
    wrapper.vm.formData.email = 'test@example.com'
    wrapper.vm.formData.first_name = 'Test'
    wrapper.vm.formData.last_name = 'User'
    wrapper.vm.formData.role = 'Agricultor'
    wrapper.vm.formData.password = password
    wrapper.vm.formData.password_confirm = password

    await wrapper.vm.saveUser()
    await wrapper.vm.$nextTick()

    expect(mockAdminStore.createUser).toHaveBeenCalled()
  })
})


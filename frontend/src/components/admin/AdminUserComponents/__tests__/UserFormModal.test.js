import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import UserFormModal from '../UserFormModal.vue'
import { generatePassword } from '@/utils/testUtils'
import {
  createMockAdminStore,
  createMockAuthStore
} from '@/test/mocks/stores'
import { createMockUseFormValidation } from '@/test/mocks/composables'

const mockAdminStore = createMockAdminStore({
  createUser: vi.fn(),
  updateUser: vi.fn()
})

const mockAuthStore = createMockAuthStore({
  user: {
    is_superuser: true
  }
})

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
  for (const key of Object.keys(mockErrors)) {
    delete mockErrors[key]
  }
})

vi.mock('@/composables/useFormValidation', () => ({
  useFormValidation: () => createMockUseFormValidation({
    errors: mockErrors,
    setError: mockSetError,
    clearErrors: mockClearErrors
  })
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn().mockResolvedValue({ isConfirmed: true })
  }
}))

const createWrapper = (props = {}) => {
  return mount(UserFormModal, {
    props,
    global: {}
  })
}

const fillFormData = (wrapper, formData) => {
  for (const [key, value] of Object.entries(formData)) {
    wrapper.vm.formData[key] = value
  }
}

const clearErrors = () => {
  for (const key of Object.keys(mockErrors)) {
    delete mockErrors[key]
  }
}

describe('UserFormModal', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    clearErrors()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render modal', () => {
    wrapper = createWrapper()
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('should display create mode title', () => {
    wrapper = createWrapper({ mode: 'create' })
    expect(wrapper.text()).toContain('Crear Usuario')
  })

  it('should display edit mode title', () => {
    wrapper = createWrapper({ mode: 'edit', user: { id: 1, username: 'test' } })
    expect(wrapper.text()).toContain('Editar Usuario')
  })

  it('should show password fields in create mode', () => {
    wrapper = createWrapper({ mode: 'create' })
    expect(wrapper.find('#password').exists()).toBe(true)
    expect(wrapper.find('#password_confirm').exists()).toBe(true)
  })

  it('should show new password fields in edit mode', () => {
    wrapper = createWrapper({ mode: 'edit', user: { id: 1 } })
    expect(wrapper.find('#new_password').exists()).toBe(true)
    expect(wrapper.find('#new_password_confirm').exists()).toBe(true)
  })

  it('should validate required fields', async () => {
    wrapper = createWrapper({ mode: 'create' })
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    fillFormData(wrapper, {
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      role: '',
      password: '',
      password_confirm: ''
    })
    
    await wrapper.vm.$nextTick()
    const isValid = wrapper.vm.validateForm()
    
    expect(isValid).toBe(false)
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

    wrapper = createWrapper({ mode: 'create' })
    const password = generatePassword()
    fillFormData(wrapper, {
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      role: 'Agricultor',
      password,
      password_confirm: password
    })

    await wrapper.vm.saveUser()
    await wrapper.vm.$nextTick()

    expect(mockAdminStore.createUser).toHaveBeenCalled()
  })

  it('should update user with valid data', async () => {
    mockAdminStore.updateUser.mockResolvedValue({
      data: { id: 1, username: 'testuser' }
    })

    wrapper = createWrapper({
      mode: 'edit',
      user: { id: 1, username: 'testuser', email: 'test@example.com', first_name: 'Test', last_name: 'User', role: 'farmer' }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    fillFormData(wrapper, {
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Updated',
      last_name: 'Name',
      role: 'farmer'
    })

    await wrapper.vm.$nextTick()
    await wrapper.vm.saveUser()
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(mockAdminStore.updateUser).toHaveBeenCalledWith(1, expect.any(Object))
  })

  it('should validate password match in create mode', async () => {
    wrapper = createWrapper({ mode: 'create' })
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const password = generatePassword()
    const differentPassword = generatePassword()
    fillFormData(wrapper, {
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      role: 'farmer',
      password,
      password_confirm: differentPassword
    })

    await wrapper.vm.$nextTick()
    const isValid = wrapper.vm.validateForm()
    
    expect(isValid).toBe(false)
    expect(wrapper.vm.errors.password_confirm).toBe('Las contraseñas no coinciden')
  })

  it('should validate new password match in edit mode', async () => {
    wrapper = createWrapper({
      mode: 'edit',
      user: { id: 1, username: 'testuser', email: 'test@example.com', first_name: 'Test', last_name: 'User', role: 'farmer' }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const newPassword = generatePassword()
    const differentPassword = generatePassword()
    fillFormData(wrapper, {
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      role: 'farmer',
      new_password: newPassword,
      new_password_confirm: differentPassword
    })

    await wrapper.vm.$nextTick()
    const isValid = wrapper.vm.validateForm()
    
    expect(isValid).toBe(false)
    expect(wrapper.vm.errors.new_password_confirm).toBe('Las contraseñas no coinciden')
  })

  it('should show superuser checkbox for superusers', () => {
    wrapper = createWrapper({ mode: 'create' })
    expect(wrapper.find('#is_superuser').exists()).toBe(true)
  })

  it('should close modal', async () => {
    wrapper = createWrapper()
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

    wrapper = createWrapper({ mode: 'edit', user })
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
    wrapper = createWrapper({ mode: 'create' })
    const password = generatePassword()
    fillFormData(wrapper, {
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      role: 'Agricultor',
      password,
      password_confirm: password
    })

    await wrapper.vm.saveUser()
    await wrapper.vm.$nextTick()

    expect(mockAdminStore.createUser).toHaveBeenCalled()
  })
})


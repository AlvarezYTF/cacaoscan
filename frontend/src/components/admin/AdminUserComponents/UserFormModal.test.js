import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import { reactive } from 'vue'

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div><slot name="header"></slot><slot></slot></div>',
    props: ['show', 'title', 'subtitle', 'maxWidth'],
    emits: ['close']
  }
}))

// Mock admin store
const mockCreateUser = vi.fn()
const mockUpdateUser = vi.fn()

vi.mock('@/stores/admin', () => {
  return {
    useAdminStore: vi.fn(() => ({
      createUser: mockCreateUser,
      updateUser: mockUpdateUser
    }))
  }
})

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    user: { is_superuser: true },
    isAdmin: true
  }))
}))

// Mock form validation composable
const mockIsValidEmail = vi.fn(() => true)
const mockIsValidPhone = vi.fn(() => true)
const mockValidatePassword = vi.fn(() => true)
const mockErrors = reactive({})
const mockSetError = vi.fn((field, message) => {
  mockErrors[field] = message
})
const mockClearErrors = vi.fn(() => {
  Object.keys(mockErrors).forEach(key => delete mockErrors[key])
})

vi.mock('@/composables/useFormValidation', () => ({
  useFormValidation: vi.fn(() => ({
    errors: mockErrors,
    isValidEmail: mockIsValidEmail,
    isValidPhone: mockIsValidPhone,
    validatePassword: mockValidatePassword,
    setError: mockSetError,
    clearErrors: mockClearErrors
  }))
}))

vi.mock('@/composables/useNotifications', () => ({
  useNotifications: vi.fn(() => ({
    showSuccess: vi.fn(),
    showError: vi.fn()
  }))
}))

import UserFormModal from './UserFormModal.vue'

describe('UserFormModal', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    Object.keys(mockErrors).forEach(key => delete mockErrors[key])
    mockIsValidEmail.mockReturnValue(true)
    mockIsValidPhone.mockReturnValue(true)
    mockValidatePassword.mockReturnValue(true)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render modal in create mode', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should render modal in edit mode', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'edit',
        user: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com'
        }
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display create user title in create mode', async () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    await wrapper.vm.$nextTick()
    
    const text = wrapper.text()
    // Check for the title in the header slot
    const headerText = wrapper.find('h3')?.text() || ''
    const allText = text + headerText
    
    expect(allText.includes('Crear') || allText.includes('Usuario')).toBe(true)
  })

  it('should emit close event when modal is closed', async () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    await wrapper.vm.closeModal()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should validate basic fields', async () => {
    mockIsValidEmail.mockReturnValue(false)

    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    wrapper.vm.formData.username = ''
    wrapper.vm.formData.email = 'invalid-email'
    wrapper.vm.formData.first_name = ''
    wrapper.vm.formData.last_name = ''
    wrapper.vm.formData.role = ''

    wrapper.vm.validateBasicFields()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.errors.username).toBeTruthy()
    expect(wrapper.vm.errors.email).toBeTruthy()
    expect(wrapper.vm.errors.first_name).toBeTruthy()
    expect(wrapper.vm.errors.last_name).toBeTruthy()
    expect(wrapper.vm.errors.role).toBeTruthy()
  })

  it('should validate username length', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    wrapper.vm.formData.username = 'ab'
    wrapper.vm.validateBasicFields()

    expect(wrapper.vm.errors.username).toBeTruthy()
  })

  it('should validate create password', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    wrapper.vm.formData.password = 'short'
    wrapper.vm.formData.password_confirm = 'different'

    wrapper.vm.validateCreatePassword()

    expect(wrapper.vm.errors.password).toBeTruthy()
    expect(wrapper.vm.errors.password_confirm).toBeTruthy()
  })

  it('should validate edit password when provided', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'edit',
        user: { id: 1, username: 'test' }
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    wrapper.vm.formData.new_password = 'short'
    wrapper.vm.formData.new_password_confirm = 'different'

    wrapper.vm.validateEditPassword()

    // Verify setError was called
    expect(mockSetError).toHaveBeenCalledWith('new_password', 'La contraseña debe tener al menos 8 caracteres')
    expect(mockSetError).toHaveBeenCalledWith('new_password_confirm', 'Las contraseñas no coinciden')
    
    // Verify errors were set in mockErrors (which should be the same reference as wrapper.vm.errors)
    expect(mockErrors.new_password).toBeTruthy()
    expect(mockErrors.new_password_confirm).toBeTruthy()
    
    // Also verify wrapper.vm.errors (they should be the same object)
    expect(wrapper.vm.errors).toBe(mockErrors)
    expect(wrapper.vm.errors.new_password).toBeTruthy()
    expect(wrapper.vm.errors.new_password_confirm).toBeTruthy()
  })

  it('should not validate edit password when not provided', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'edit',
        user: { id: 1, username: 'test' }
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    wrapper.vm.formData.new_password = ''
    wrapper.vm.validateEditPassword()

    expect(wrapper.vm.errors.new_password).toBeFalsy()
  })

  it('should validate phone number when provided', () => {
    mockIsValidPhone.mockReturnValue(false)

    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    wrapper.vm.formData.phone = '123'
    wrapper.vm.validateForm()

    expect(wrapper.vm.errors.phone).toBeTruthy()
  })

  it('should build user data for create mode', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    wrapper.vm.formData.username = 'testuser'
    wrapper.vm.formData.email = 'test@test.com'
    wrapper.vm.formData.first_name = 'Test'
    wrapper.vm.formData.last_name = 'User'
    wrapper.vm.formData.role = 'admin'
    wrapper.vm.formData.phone = '1234567890'
    wrapper.vm.formData.location = 'Location'
    wrapper.vm.formData.organization = 'Org'
    wrapper.vm.formData.is_active = true
    wrapper.vm.formData.is_staff = false
    wrapper.vm.formData.is_superuser = false
    wrapper.vm.formData.notes = 'Notes'
    wrapper.vm.formData.password = 'password123'

    const userData = wrapper.vm.buildUserData()

    expect(userData.username).toBe('testuser')
    expect(userData.password).toBe('password123')
  })

  it('should build user data for edit mode with new password', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'edit',
        user: { id: 1, username: 'test' }
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    wrapper.vm.formData.new_password = 'newpassword123'

    const userData = wrapper.vm.buildUserData()

    expect(userData.password).toBe('newpassword123')
  })

  it('should process user errors from API', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    const errorData = {
      username: ['Username already exists'],
      email: ['Email already exists'],
      password: ['Password too weak']
    }

    wrapper.vm.processUserErrors(errorData)

    expect(wrapper.vm.errors.username).toBe('Username already exists')
    expect(wrapper.vm.errors.email).toBe('Email already exists')
    expect(wrapper.vm.errors.password).toBe('Password too weak')
  })

  it('should save user in create mode', async () => {
    mockCreateUser.mockResolvedValue({ data: { id: 1 } })

    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    wrapper.vm.formData.username = 'testuser'
    wrapper.vm.formData.email = 'test@test.com'
    wrapper.vm.formData.first_name = 'Test'
    wrapper.vm.formData.last_name = 'User'
    wrapper.vm.formData.role = 'admin'
    wrapper.vm.formData.password = 'password123'
    wrapper.vm.formData.password_confirm = 'password123'
    
    // Ensure errors object is empty and validation will pass
    mockErrors.value = {}
    await wrapper.vm.$nextTick()

    await wrapper.vm.saveUser()
    await wrapper.vm.$nextTick()

    expect(mockCreateUser).toHaveBeenCalled()
    expect(wrapper.emitted('saved')).toBeTruthy()
  })

  it('should save user in edit mode', async () => {
    mockUpdateUser.mockResolvedValue({ data: { id: 1 } })

    wrapper = mount(UserFormModal, {
      props: {
        mode: 'edit',
        user: { id: 1, username: 'test' }
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    await wrapper.vm.$nextTick()

    // Clear any errors and set valid form data
    mockErrors.value = {}
    mockClearErrors()
    wrapper.vm.formData.username = 'testuser'
    wrapper.vm.formData.email = 'test@test.com'
    wrapper.vm.formData.first_name = 'Test'
    wrapper.vm.formData.last_name = 'User'
    wrapper.vm.formData.role = 'admin'
    
    // Store original validateForm and replace with mock
    const originalValidateForm = wrapper.vm.validateForm
    wrapper.vm.validateForm = () => {
      mockClearErrors()
      return true
    }

    await wrapper.vm.saveUser()
    await wrapper.vm.$nextTick()

    expect(mockUpdateUser).toHaveBeenCalled()
    expect(wrapper.emitted('saved')).toBeTruthy()
    
    // Restore original function
    wrapper.vm.validateForm = originalValidateForm
  })

  it('should handle error when saving user', async () => {
    mockCreateUser.mockRejectedValue({
      response: {
        data: {
          username: ['Username already exists']
        }
      }
    })

    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    wrapper.vm.formData.username = 'testuser'
    wrapper.vm.formData.email = 'test@test.com'
    wrapper.vm.formData.first_name = 'Test'
    wrapper.vm.formData.last_name = 'User'
    wrapper.vm.formData.role = 'admin'
    wrapper.vm.formData.password = 'password123'
    wrapper.vm.formData.password_confirm = 'password123'
    wrapper.vm.validateForm = vi.fn().mockReturnValue(true)

    await wrapper.vm.saveUser()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.errors.username).toBe('Username already exists')
  })

  it('should handle error without response', async () => {
    mockCreateUser.mockRejectedValue(new Error('Network error'))

    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    wrapper.vm.formData.username = 'testuser'
    wrapper.vm.formData.email = 'test@test.com'
    wrapper.vm.formData.first_name = 'Test'
    wrapper.vm.formData.last_name = 'User'
    wrapper.vm.formData.role = 'admin'
    wrapper.vm.formData.password = 'password123'
    wrapper.vm.formData.password_confirm = 'password123'
    wrapper.vm.validateForm = vi.fn().mockReturnValue(true)

    await wrapper.vm.saveUser()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.loading).toBe(false)
  })

  it('should initialize form when user prop changes', async () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'edit',
        user: { id: 1, username: 'test', email: 'test@test.com' }
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.setProps({ user: { id: 2, username: 'test2', email: 'test2@test.com' } })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.formData.username).toBe('test2')
  })

  it('should initialize form when mode prop changes', async () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.setProps({ mode: 'edit', user: { id: 1, username: 'test' } })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.formData.username).toBe('test')
  })
})


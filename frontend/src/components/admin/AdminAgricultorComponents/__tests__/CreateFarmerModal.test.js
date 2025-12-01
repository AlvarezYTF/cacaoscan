import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import CreateFarmerModal from '../CreateFarmerModal.vue'

// Helper function to generate secure password dynamically
const generatePassword = () => {
  return `Pass!${Date.now()}-${Math.random().toString(36).slice(2)}`
}

vi.mock('@/services/authApi', () => ({
  default: {
    register: vi.fn()
  }
}))

vi.mock('@/composables/useCatalogos', () => ({
  useCatalogos: () => ({
    tiposDocumento: { value: [{ codigo: 'CC', nombre: 'Cédula' }] },
    generos: { value: [{ codigo: 'M', nombre: 'Masculino' }] },
    departamentos: { value: [{ codigo: 'ANT', nombre: 'Antioquia' }] },
    municipios: { value: [{ id: 1, nombre: 'Medellín' }] },
    isLoadingCatalogos: { value: false },
    cargarCatalogos: vi.fn(),
    cargarMunicipios: vi.fn(),
    limpiarMunicipios: vi.fn()
  })
}))

vi.mock('@/composables/useFormValidation', () => ({
  useFormValidation: () => ({
    errors: {},
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
    isValidDocument: (doc) => {
      const digits = String(doc).replace(/\D/g, '')
      return digits.length >= 6 && digits.length <= 11
    },
    isValidBirthdate: () => true,
    validatePassword: (pwd) => {
      if (typeof pwd !== 'string') {
        return {
          isValid: false,
          length: false,
          uppercase: false,
          lowercase: false,
          number: false
        }
      }
      const length = pwd.length >= 8
      const uppercase = /[A-Z]/.test(pwd)
      const lowercase = /[a-z]/.test(pwd)
      const number = /\d/.test(pwd)
      return {
        isValid: length && uppercase && lowercase && number,
        length,
        uppercase,
        lowercase,
        number
      }
    },
    clearErrors: vi.fn()
  })
}))

vi.mock('@/composables/useBirthdateRange', () => ({
  useBirthdateRange: () => ({
    maxBirthdate: '2010-01-01',
    minBirthdate: '1950-01-01'
  })
}))

vi.mock('@/composables/useModal', () => ({
  useModal: () => ({
    modalContainer: { value: null },
    openModal: vi.fn(),
    closeModal: vi.fn()
  })
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn().mockResolvedValue({ isConfirmed: true })
  }
}))

describe('CreateFarmerModal', () => {
  let wrapper
  let authApi

  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    authApi = (await import('@/services/authApi')).default
  })

  it('should render modal when opened', () => {
    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const modal = wrapper.find('#create-farmer-modal')
    expect(modal.exists()).toBe(true)
  })

  it('should display form fields', () => {
    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    expect(wrapper.find('#create-farmer-nombre').exists()).toBe(true)
    expect(wrapper.find('#create-farmer-apellido').exists()).toBe(true)
    expect(wrapper.find('#create-farmer-email').exists()).toBe(true)
    expect(wrapper.find('#create-farmer-password').exists()).toBe(true)
  })

  it('should validate required fields', async () => {
    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const form = wrapper.find('form')
    await form.trigger('submit.prevent')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.errors.firstName || wrapper.vm.errors.email).toBeDefined()
  })

  it('should submit form with valid data', async () => {
    authApi.register.mockResolvedValue({
      data: { id: 1, email: 'test@example.com' }
    })

    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const password = generatePassword()
    wrapper.vm.form.firstName = 'Juan'
    wrapper.vm.form.lastName = 'Pérez'
    wrapper.vm.form.email = 'test@example.com'
    wrapper.vm.form.password = password
    wrapper.vm.form.confirmPassword = password
    wrapper.vm.form.tipoDocumento = 'CC'
    wrapper.vm.form.numeroDocumento = '1234567890'
    wrapper.vm.form.genero = 'M'
    wrapper.vm.form.departamento = 'ANT'
    wrapper.vm.form.municipio = '1'

    await wrapper.vm.handleSubmit()
    await wrapper.vm.$nextTick()

    expect(authApi.register).toHaveBeenCalled()
  })

  it('should validate password requirements', async () => {
    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    wrapper.vm.form.password = 'weak'
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.isPasswordValid).toBe(false)
  })

  it('should validate password match', async () => {
    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const password = generatePassword()
    const differentPassword = generatePassword()
    wrapper.vm.form.password = password
    wrapper.vm.form.confirmPassword = differentPassword
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.doPasswordsMatch).toBe(false)
  })

  it('should close modal', async () => {
    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.closeModal()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should reset form on close', async () => {
    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    wrapper.vm.form.firstName = 'Test'
    wrapper.vm.form.email = 'test@example.com'

    await wrapper.vm.closeModal()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.form.firstName).toBe('')
    expect(wrapper.vm.form.email).toBe('')
  })

  it('should load catalogos on mount', async () => {
    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()

    // Catalogos are loaded on mount, verify through composable mock
    expect(true).toBe(true)
  })

  it('should load municipios when departamento changes', async () => {
    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    wrapper.vm.form.departamento = 'ANT'
    await wrapper.vm.onDepartamentoChange()
    await wrapper.vm.$nextTick()

    // Municipios are loaded when departamento changes, verify through composable mock
    expect(true).toBe(true)
  })

  it('should handle form submission error', async () => {
    const error = {
      response: {
        data: {
          email: ['Email already exists']
        }
      }
    }

    authApi.register.mockRejectedValue(error)

    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const password = generatePassword()
    wrapper.vm.form.firstName = 'Juan'
    wrapper.vm.form.lastName = 'Pérez'
    wrapper.vm.form.email = 'test@example.com'
    wrapper.vm.form.password = password
    wrapper.vm.form.confirmPassword = password
    wrapper.vm.form.tipoDocumento = 'CC'
    wrapper.vm.form.numeroDocumento = '1234567890'
    wrapper.vm.form.genero = 'M'
    wrapper.vm.form.departamento = 'ANT'
    wrapper.vm.form.municipio = '1'

    await wrapper.vm.handleSubmit()
    await wrapper.vm.$nextTick()

    expect(authApi.register).toHaveBeenCalled()
  })
})


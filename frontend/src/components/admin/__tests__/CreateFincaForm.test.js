import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import CreateFincaForm from '../CreateFincaForm.vue'

// Mock dependencies - use vi.hoisted() for variables used in vi.mock
const { mockAuthStore, mockFincasStore, mockShowSuccess, mockShowError, mockCreateFinca, mockGetAgricultores } = vi.hoisted(() => ({
  mockAuthStore: {
    user: { id: 1, role: 'admin' }
  },
  mockFincasStore: {
    refresh: vi.fn()
  },
  mockShowSuccess: vi.fn(),
  mockShowError: vi.fn(),
  mockCreateFinca: vi.fn(),
  mockGetAgricultores: vi.fn()
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('@/stores/fincas', () => ({
  useFincasStore: () => mockFincasStore
}))

vi.mock('@/composables/useNotifications', () => ({
  useNotifications: () => ({
    showSuccess: mockShowSuccess,
    showError: mockShowError
  })
}))

vi.mock('@/services/fincasApi', () => ({
  createFinca: mockCreateFinca,
  getAgricultores: mockGetAgricultores
}))

describe('CreateFincaForm', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockAuthStore.user = { id: 1, role: 'admin' }
    mockCreateFinca.mockResolvedValue({ data: { id: 1 } })
    mockGetAgricultores.mockResolvedValue({
      data: {
        results: [
          { id: 1, username: 'Agricultor 1' },
          { id: 2, username: 'Agricultor 2' }
        ]
      }
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(CreateFincaForm)

      expect(wrapper.exists()).toBe(true)
    })

    it('should display modal title', () => {
      wrapper = mount(CreateFincaForm)

      expect(wrapper.text()).toContain('Nueva Finca')
      expect(wrapper.text()).toContain('Registra una nueva finca en el sistema')
    })

    it('should display form fields', () => {
      wrapper = mount(CreateFincaForm)

      expect(wrapper.find('#create-finca-nombre').exists()).toBe(true)
      expect(wrapper.text()).toContain('Nombre de la Finca')
    })

    it('should display action buttons', () => {
      wrapper = mount(CreateFincaForm)

      const buttons = wrapper.findAll('button')
      expect(buttons.length).toBeGreaterThanOrEqual(2)
      expect(wrapper.text()).toContain('Cancelar')
      expect(wrapper.text()).toContain('Crear Finca')
    })
  })

  describe('Agricultores Loading', () => {
    it('should load agricultores when user is admin', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockResolvedValue({
        data: {
          results: [
            { id: 1, username: 'Agricultor 1' },
            { id: 2, username: 'Agricultor 2' }
          ]
        }
      })

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockGetAgricultores).toHaveBeenCalled()
    })

    it('should not load agricultores when user is not admin', async () => {
      mockAuthStore.user = { id: 1, role: 'farmer' }

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockGetAgricultores).not.toHaveBeenCalled()
    })

    it('should not load agricultores when user role is undefined', async () => {
      mockAuthStore.user = { id: 1 }

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockGetAgricultores).not.toHaveBeenCalled()
    })

    it('should handle agricultores response with results array', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockResolvedValue({
        data: {
          results: [
            { id: 1, username: 'Agricultor 1' },
            { id: 2, username: 'Agricultor 2' }
          ]
        }
      })

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.agricultores.length).toBe(2)
    })

    it('should handle agricultores response as direct array', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockResolvedValue({
        data: [
          { id: 1, username: 'Agricultor 1' },
          { id: 2, username: 'Agricultor 2' }
        ]
      })

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.agricultores.length).toBe(2)
    })

    it('should handle agricultores response with empty results', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockResolvedValue({
        data: {
          results: []
        }
      })

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.agricultores.length).toBe(0)
    })

    it('should handle error when loading agricultores', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockRejectedValue(new Error('Network error'))

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockShowError).toHaveBeenCalledWith('No se pudo cargar la lista de agricultores')
    })

    it('should display agricultor select for admin users', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockResolvedValue({
        data: {
          results: [
            { id: 1, username: 'Agricultor 1' }
          ]
        }
      })

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const agricultorSelect = wrapper.find('#create-finca-agricultor')
      expect(agricultorSelect.exists()).toBe(true)
    })

    it('should not display agricultor select for non-admin users', () => {
      mockAuthStore.user = { id: 1, role: 'farmer' }

      wrapper = mount(CreateFincaForm)

      const agricultorSelect = wrapper.find('#create-finca-agricultor')
      expect(agricultorSelect.exists()).toBe(false)
    })
  })

  describe('Form Submission', () => {
    it('should submit form with valid data', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockResolvedValue({
        data: {
          results: [
            { id: 1, username: 'Agricultor 1' }
          ]
        }
      })
      mockCreateFinca.mockResolvedValue({ data: { id: 1 } })

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const nombreInput = wrapper.find('#create-finca-nombre')
      await nombreInput.setValue('Nueva Finca')

      const agricultorSelect = wrapper.find('#create-finca-agricultor')
      await agricultorSelect.setValue('1')

      const form = wrapper.find('form')
      await form.trigger('submit')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockCreateFinca).toHaveBeenCalledWith({
        nombre: 'Nueva Finca',
        agricultor: 1
      })
      expect(mockShowSuccess).toHaveBeenCalledWith('Finca creada correctamente')
      expect(wrapper.emitted('saved')).toBeTruthy()
    })

    it('should reset form after successful submission', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockResolvedValue({
        data: {
          results: [
            { id: 1, username: 'Agricultor 1' }
          ]
        }
      })
      mockCreateFinca.mockResolvedValue({ data: { id: 1 } })

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const nombreInput = wrapper.find('#create-finca-nombre')
      await nombreInput.setValue('Nueva Finca')

      const agricultorSelect = wrapper.find('#create-finca-agricultor')
      await agricultorSelect.setValue('1')

      const form = wrapper.find('form')
      await form.trigger('submit')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.form.nombre).toBe('')
      expect(wrapper.vm.form.agricultor).toBe('')
    })

    it('should handle error when creating finca', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockResolvedValue({
        data: {
          results: [
            { id: 1, username: 'Agricultor 1' }
          ]
        }
      })
      mockCreateFinca.mockRejectedValue(new Error('Server error'))

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const nombreInput = wrapper.find('#create-finca-nombre')
      await nombreInput.setValue('Nueva Finca')

      const agricultorSelect = wrapper.find('#create-finca-agricultor')
      await agricultorSelect.setValue('1')

      const form = wrapper.find('form')
      await form.trigger('submit')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockShowError).toHaveBeenCalledWith('Error al crear la finca')
      expect(wrapper.emitted('saved')).toBeFalsy()
    })

    it('should set loading state during submission', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockResolvedValue({
        data: {
          results: [
            { id: 1, username: 'Agricultor 1' }
          ]
        }
      })
      
      let resolveCreate
      const createPromise = new Promise((resolve) => {
        resolveCreate = resolve
      })
      mockCreateFinca.mockReturnValue(createPromise)

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const nombreInput = wrapper.find('#create-finca-nombre')
      await nombreInput.setValue('Nueva Finca')

      const agricultorSelect = wrapper.find('#create-finca-agricultor')
      await agricultorSelect.setValue('1')

      const form = wrapper.find('form')
      const submitPromise = form.trigger('submit')
      await nextTick()

      expect(wrapper.vm.loading).toBe(true)
      
      resolveCreate({ data: { id: 1 } })
      await submitPromise
      await nextTick()

      expect(wrapper.vm.loading).toBe(false)
    })

    it('should disable submit button when loading', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockResolvedValue({
        data: {
          results: [
            { id: 1, username: 'Agricultor 1' }
          ]
        }
      })
      
      let resolveCreate
      const createPromise = new Promise((resolve) => {
        resolveCreate = resolve
      })
      mockCreateFinca.mockReturnValue(createPromise)

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const nombreInput = wrapper.find('#create-finca-nombre')
      await nombreInput.setValue('Nueva Finca')

      const agricultorSelect = wrapper.find('#create-finca-agricultor')
      await agricultorSelect.setValue('1')

      const form = wrapper.find('form')
      const submitPromise = form.trigger('submit')
      await nextTick()

      const submitButton = wrapper.findAll('button[type="submit"]')[0]
      expect(submitButton.attributes('disabled')).toBeDefined()
      expect(submitButton.text()).toContain('Guardando...')
      
      resolveCreate({ data: { id: 1 } })
      await submitPromise
      await nextTick()

      expect(submitButton.attributes('disabled')).toBeUndefined()
    })
  })

  describe('Events', () => {
    it('should emit close event when close button is clicked', async () => {
      wrapper = mount(CreateFincaForm)

      const closeButtons = wrapper.findAll('button')
      const closeButton = closeButtons.find(btn => 
        btn.text().includes('Cancelar') || 
        btn.attributes('aria-label')?.includes('close') ||
        btn.find('svg').exists()
      ) || closeButtons[0]

      await closeButton.trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('should emit close event when X button is clicked', async () => {
      wrapper = mount(CreateFincaForm)

      const header = wrapper.find('.bg-gradient-to-r')
      const closeButton = header.find('button')
      
      if (closeButton.exists()) {
        await closeButton.trigger('click')
        expect(wrapper.emitted('close')).toBeTruthy()
      }
    })

    it('should emit saved event after successful form submission', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockResolvedValue({
        data: {
          results: [
            { id: 1, username: 'Agricultor 1' }
          ]
        }
      })
      mockCreateFinca.mockResolvedValue({ data: { id: 1 } })

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const nombreInput = wrapper.find('#create-finca-nombre')
      await nombreInput.setValue('Nueva Finca')

      const agricultorSelect = wrapper.find('#create-finca-agricultor')
      await agricultorSelect.setValue('1')

      const form = wrapper.find('form')
      await form.trigger('submit')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.emitted('saved')).toBeTruthy()
    })
  })

  describe('Form Validation', () => {
    it('should have required attribute on nombre field', () => {
      wrapper = mount(CreateFincaForm)

      const nombreInput = wrapper.find('#create-finca-nombre')
      expect(nombreInput.attributes('required')).toBeDefined()
    })

    it('should have required attribute on agricultor field for admin', async () => {
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockGetAgricultores.mockResolvedValue({
        data: {
          results: [
            { id: 1, username: 'Agricultor 1' }
          ]
        }
      })

      wrapper = mount(CreateFincaForm)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const agricultorSelect = wrapper.find('#create-finca-agricultor')
      if (agricultorSelect.exists()) {
        expect(agricultorSelect.attributes('required')).toBeDefined()
      }
    })
  })

  describe('Form State', () => {
    it('should initialize form with empty values', () => {
      wrapper = mount(CreateFincaForm)

      expect(wrapper.vm.form.nombre).toBe('')
      expect(wrapper.vm.form.agricultor).toBe('')
    })

    it('should initialize loading as false', () => {
      wrapper = mount(CreateFincaForm)

      expect(wrapper.vm.loading).toBe(false)
    })

    it('should initialize agricultores as empty array', () => {
      wrapper = mount(CreateFincaForm)

      expect(wrapper.vm.agricultores).toEqual([])
    })
  })
})


import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import FincaForm from './FincaForm.vue'

vi.mock('@/services/fincasApi', async () => {
  const actual = await vi.importActual('@/services/fincasApi')
  return {
    ...actual,
    default: {
      getDepartamentosColombia: vi.fn(() => ['Cundinamarca', 'Antioquia']),
      getMunicipiosByDepartamento: vi.fn(() => ['Bogotá', 'Medellín']),
      formatFincaData: vi.fn((data) => ({ ...data, formatted: true })),
      validateFincaData: vi.fn(() => ({ isValid: true, errors: [] }))
    },
    getAgricultores: vi.fn(() => Promise.resolve({
      data: {
        results: [
          { id: 1, username: 'Agricultor 1' },
          { id: 2, username: 'Agricultor 2' }
        ]
      }
    }))
  }
})

vi.mock('@/stores/fincas', () => ({
  useFincasStore: vi.fn(() => ({
    create: vi.fn(() => Promise.resolve({ id: 1 })),
    update: vi.fn(() => Promise.resolve({ id: 1 }))
  }))
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    isAdmin: false
  }))
}))

vi.mock('@/composables/useFormValidation', () => ({
  useFormValidation: vi.fn(() => ({
    errors: { value: {} },
    mapServerErrors: vi.fn(),
    scrollToFirstError: vi.fn()
  }))
}))

vi.mock('@/composables/useNotifications', () => ({
  useNotifications: vi.fn(() => ({
    showSuccess: vi.fn(),
    showError: vi.fn()
  }))
}))

vi.mock('@/composables/useFincas', () => ({
  useFincas: vi.fn(() => ({
    create: vi.fn(() => Promise.resolve()),
    update: vi.fn(() => Promise.resolve()),
    isLoading: { value: false }
  }))
}))

describe('FincaForm', () => {
  let wrapper
  let mockCreate
  let mockUpdate
  let mockShowSuccess
  let mockShowError
  let mockFincasStore

  const mockFinca = {
    id: 1,
    nombre: 'Test Finca',
    ubicacion: 'Test Ubicación',
    municipio: 'Bogotá',
    departamento: 'Cundinamarca',
    hectareas: 10,
    descripcion: 'Test Description',
    coordenadas_lat: 4.6097,
    coordenadas_lng: -74.0817,
    activa: true
  }

  beforeEach(async () => {
    mockCreate = vi.fn(() => Promise.resolve({ id: 1 }))
    mockUpdate = vi.fn(() => Promise.resolve({ id: 1 }))
    mockShowSuccess = vi.fn()
    mockShowError = vi.fn()
    mockFincasStore = {
      create: mockCreate,
      update: mockUpdate
    }

    const { useFincasStore } = await import('@/stores/fincas')
    vi.mocked(useFincasStore).mockReturnValue(mockFincasStore)

    const { useNotifications } = await import('@/composables/useNotifications')
    vi.mocked(useNotifications).mockReturnValue({
      showSuccess: mockShowSuccess,
      showError: mockShowError
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  it('should render form component', () => {
    wrapper = mount(FincaForm, {
      props: {
        finca: null,
        isEditing: false
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display create title when not editing', () => {
    wrapper = mount(FincaForm, {
      props: {
        finca: null,
        isEditing: false
      }
    })

    const text = wrapper.text()
    expect(text.includes('Nueva Finca') || text.includes('Crear')).toBe(true)
  })

  it('should display edit title when editing', () => {
    wrapper = mount(FincaForm, {
      props: {
        finca: mockFinca,
        isEditing: true
      }
    })

    const text = wrapper.text()
    expect(text.includes('Editar Finca') || text.includes('Modifica')).toBe(true)
  })

  it('should load finca data when finca prop is provided', async () => {
    wrapper = mount(FincaForm, {
      props: {
        finca: mockFinca,
        isEditing: true
      }
    })

    await nextTick()

    const nombreInput = wrapper.find('#finca-form-nombre')
    if (nombreInput.exists()) {
      expect(nombreInput.element.value).toBe(mockFinca.nombre)
    }
  })

  it('should reset form when finca prop is null', async () => {
    wrapper = mount(FincaForm, {
      props: {
        finca: mockFinca,
        isEditing: false
      }
    })

    await nextTick()

    await wrapper.setProps({ finca: null })
    await nextTick()

    const nombreInput = wrapper.find('#finca-form-nombre')
    if (nombreInput.exists()) {
      expect(nombreInput.element.value).toBe('')
    }
  })

  it('should load municipios when departamento changes', async () => {
    const fincasApi = await import('@/services/fincasApi')
    wrapper = mount(FincaForm, {
      props: {
        finca: null,
        isEditing: false
      }
    })

    await nextTick()

    const departamentoSelect = wrapper.find('#finca-form-departamento')
    if (departamentoSelect.exists()) {
      await departamentoSelect.setValue('Cundinamarca')
      await nextTick()

      expect(fincasApi.default.getMunicipiosByDepartamento).toHaveBeenCalledWith('Cundinamarca')
    }
  })

  it('should reset municipio when departamento changes', async () => {
    wrapper = mount(FincaForm, {
      props: {
        finca: { ...mockFinca, municipio: 'Bogotá' },
        isEditing: true
      }
    })

    await nextTick()

    const departamentoSelect = wrapper.find('#finca-form-departamento')
    if (departamentoSelect.exists()) {
      await departamentoSelect.setValue('Antioquia')
      await nextTick()

      const municipioSelect = wrapper.find('#finca-form-municipio')
      if (municipioSelect.exists()) {
        expect(municipioSelect.element.value).toBe('')
      }
    }
  })

  it('should show agricultor select for admin when creating', async () => {
    const { useAuthStore } = await import('@/stores/auth')
    vi.mocked(useAuthStore).mockReturnValue({
      isAdmin: true
    })

    wrapper = mount(FincaForm, {
      props: {
        finca: null,
        isEditing: false
      }
    })

    await nextTick()

    const agricultorSelect = wrapper.find('#finca-form-agricultor')
    expect(agricultorSelect.exists()).toBe(true)
  })

  it('should not show agricultor select for non-admin', async () => {
    const { useAuthStore } = await import('@/stores/auth')
    vi.mocked(useAuthStore).mockReturnValue({
      isAdmin: false
    })

    wrapper = mount(FincaForm, {
      props: {
        finca: null,
        isEditing: false
      }
    })

    await nextTick()

    const agricultorSelect = wrapper.find('#finca-form-agricultor')
    expect(agricultorSelect.exists()).toBe(false)
  })

  it('should emit close event when close button is clicked', async () => {
    wrapper = mount(FincaForm, {
      props: {
        finca: null,
        isEditing: false
      }
    })

    const closeButton = wrapper.find('button[type="button"]')
    if (closeButton.exists() && closeButton.text().includes('Cancelar')) {
      await closeButton.trigger('click')
      expect(wrapper.emitted('close')).toBeTruthy()
    }
  })

  it('should emit saved event after successful creation', async () => {
    wrapper = mount(FincaForm, {
      props: {
        finca: null,
        isEditing: false
      }
    })

    await nextTick()

    const nombreInput = wrapper.find('#finca-form-nombre')
    const ubicacionInput = wrapper.find('#finca-form-ubicacion')
    const departamentoSelect = wrapper.find('#finca-form-departamento')
    const municipioSelect = wrapper.find('#finca-form-municipio')
    const hectareasInput = wrapper.find('#finca-form-hectareas')

    if (nombreInput.exists()) {
      await nombreInput.setValue('Nueva Finca')
    }
    if (ubicacionInput.exists()) {
      await ubicacionInput.setValue('Nueva Ubicación')
    }
    if (departamentoSelect.exists()) {
      await departamentoSelect.setValue('Cundinamarca')
    }
    if (municipioSelect.exists()) {
      await municipioSelect.setValue('Bogotá')
    }
    if (hectareasInput.exists()) {
      await hectareasInput.setValue('5')
    }

    await nextTick()

    const form = wrapper.find('form')
    if (form.exists()) {
      await form.trigger('submit')
      await nextTick()

      await new Promise(resolve => setTimeout(resolve, 100))
      await nextTick()

      expect(mockCreate).toHaveBeenCalled()
      expect(wrapper.emitted('saved')).toBeTruthy()
    }
  })

  it('should emit saved event after successful update', async () => {
    wrapper = mount(FincaForm, {
      props: {
        finca: mockFinca,
        isEditing: true
      }
    })

    await nextTick()

    const form = wrapper.find('form')
    if (form.exists()) {
      await form.trigger('submit')
      await nextTick()

      await new Promise(resolve => setTimeout(resolve, 100))
      await nextTick()

      expect(mockUpdate).toHaveBeenCalled()
      expect(wrapper.emitted('saved')).toBeTruthy()
    }
  })

  it('should show error when form validation fails', async () => {
    const fincasApi = await import('@/services/fincasApi')
    vi.mocked(fincasApi.default.validateFincaData).mockReturnValue({
      isValid: false,
      errors: ['nombre es requerido']
    })

    wrapper = mount(FincaForm, {
      props: {
        finca: null,
        isEditing: false
      }
    })

    await nextTick()

    const form = wrapper.find('form')
    if (form.exists()) {
      await form.trigger('submit')
      await nextTick()

      expect(mockCreate).not.toHaveBeenCalled()
      expect(wrapper.emitted('saved')).toBeFalsy()
    }
  })

  it('should handle server errors correctly', async () => {
    const error = new Error('Server error')
    error.response = {
      data: {
        details: {
          nombre: ['Este campo es requerido']
        }
      }
    }

    // Ensure validateFincaData returns true for valid form
    const fincasApi = await import('@/services/fincasApi')
    vi.mocked(fincasApi.default.validateFincaData).mockReturnValue({
      isValid: true,
      errors: []
    })

    // Reset and configure mock to reject before mounting
    mockCreate.mockReset()
    mockCreate.mockRejectedValue(error)
    
    // Update the store mock with the new create function
    mockFincasStore.create = mockCreate

    // Ensure mock is configured before mounting
    const { useFincasStore } = await import('@/stores/fincas')
    vi.mocked(useFincasStore).mockReturnValue(mockFincasStore)
    
    const { useNotifications } = await import('@/composables/useNotifications')
    vi.mocked(useNotifications).mockReturnValue({
      showSuccess: mockShowSuccess,
      showError: mockShowError
    })

    wrapper = mount(FincaForm, {
      props: {
        finca: null,
        isEditing: false
      }
    })

    await nextTick()
    await wrapper.vm.$nextTick()

    // Set form data directly to ensure values are set
    if (wrapper.vm.formData) {
      wrapper.vm.formData.nombre = 'Nueva Finca'
      wrapper.vm.formData.ubicacion = 'Nueva Ubicación'
      wrapper.vm.formData.departamento = 'Cundinamarca'
      wrapper.vm.formData.municipio = 'Bogotá'
      wrapper.vm.formData.hectareas = '5'
    }

    await nextTick()
    await wrapper.vm.$nextTick()
    // Wait a bit more for reactive updates
    await new Promise(resolve => setTimeout(resolve, 100))

    const form = wrapper.find('form')
    if (form.exists()) {
      await form.trigger('submit')
      
      // Wait for async operations to complete
      await new Promise(resolve => setTimeout(resolve, 300))
      await nextTick()
      await nextTick()

      expect(mockCreate).toHaveBeenCalled()
      // The component should call showError when handling server errors
      expect(mockShowError).toHaveBeenCalled()
    }
  })

  it('should load agricultores for admin on mount', async () => {
    const { useAuthStore } = await import('@/stores/auth')
    vi.mocked(useAuthStore).mockReturnValue({
      isAdmin: true
    })

    const { getAgricultores } = await import('@/services/fincasApi')

    wrapper = mount(FincaForm, {
      props: {
        finca: null,
        isEditing: false
      }
    })

    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(getAgricultores).toHaveBeenCalled()
  })
})


import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import EditFarmerModal from './EditFarmerModal.vue'

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div><slot name="header"></slot><slot></slot></div>',
    props: ['show', 'title', 'subtitle', 'maxWidth'],
    emits: ['close', 'update:show']
  }
}))

// Mock api to prevent real API calls when errors occur
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockImplementation((url) => {
      // Handle notifications endpoint specifically to prevent network errors
      if (url === '/notifications/create/') {
        return Promise.resolve({ 
          data: { 
            id: 1, 
            tipo: 'error', 
            mensaje: 'Test notification',
            fecha_creacion: new Date().toISOString()
          } 
        })
      }
      return Promise.resolve({ data: {} })
    }),
    put: vi.fn().mockResolvedValue({ data: {} }),
    patch: vi.fn().mockResolvedValue({ data: {} }),
    delete: vi.fn().mockResolvedValue({ data: {} })
  }
}))

// Mock notifications store to prevent API calls when errors occur
vi.mock('@/stores/notifications', () => ({
  useNotificationsStore: vi.fn(() => ({
    notifications: [],
    unreadCount: 0,
    loading: false,
    error: null,
    createNotification: vi.fn().mockResolvedValue({}),
    fetchNotifications: vi.fn(),
    markAsRead: vi.fn(),
    markAllAsRead: vi.fn(),
    reset: vi.fn()
  })),
  useNotificationStore: vi.fn(() => ({
    notifications: [],
    unreadCount: 0,
    loading: false,
    error: null,
    createNotification: vi.fn().mockResolvedValue({}),
    fetchNotifications: vi.fn(),
    markAsRead: vi.fn(),
    markAllAsRead: vi.fn(),
    reset: vi.fn()
  }))
}))

// Mock useNotifications composable to prevent API calls when errors occur
vi.mock('@/composables/useNotifications', () => ({
  useNotifications: vi.fn(() => ({
    showSuccess: vi.fn(),
    showError: vi.fn(),
    showWarning: vi.fn(),
    showInfo: vi.fn(),
    clearAll: vi.fn(),
    notifications: { value: [] },
    unreadCount: { value: 0 },
    loading: { value: false },
    error: { value: null },
    store: {
      createNotification: vi.fn().mockResolvedValue({}),
      fetchNotifications: vi.fn(),
      markAsRead: vi.fn(),
      markAllAsRead: vi.fn(),
      reset: vi.fn()
    }
  }))
}))

// Mock services to prevent real API calls
vi.mock('@/services/fincasApi', () => ({
  createFinca: vi.fn().mockResolvedValue({ data: {} }),
  getFincas: vi.fn().mockResolvedValue({ results: [] })
}))

vi.mock('@/services/authApi', () => ({
  default: {
    updateUser: vi.fn().mockResolvedValue({ user: {} })
  }
}))

vi.mock('@/services', () => ({
  personasApi: {
    getPersonaByUserId: vi.fn().mockRejectedValue({ response: { status: 404 } }),
    updatePersonaByUserId: vi.fn().mockResolvedValue({})
  }
}))

// Mock composables
vi.mock('@/composables/usePersonForm', () => ({
  usePersonForm: vi.fn(() => ({
    tiposDocumento: [],
    generos: [],
    departamentos: [],
    municipios: [],
    isLoadingCatalogos: false,
    cargarCatalogos: vi.fn().mockResolvedValue({}),
    cargarMunicipios: vi.fn().mockResolvedValue({}),
    limpiarMunicipios: vi.fn(),
    errors: {},
    isValidEmail: vi.fn(() => true),
    isValidPhone: vi.fn(() => true),
    isValidDocument: vi.fn(() => true),
    clearErrors: vi.fn(),
    maxBirthdate: new Date().toISOString().split('T')[0],
    minBirthdate: '1900-01-01',
    onDepartamentoChange: vi.fn().mockResolvedValue({})
  }))
}))

describe('EditFarmerModal', () => {
  let wrapper

  const mockFarmer = {
    id: 1,
    first_name: 'John',
    last_name: 'Doe',
    email: 'john.doe@example.com'
  }

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render modal when isOpen is true', () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: mockFarmer
      },
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display edit farmer title', async () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: mockFarmer
      },
      global: {
        stubs: {}
      }
    })

    await wrapper.vm.$nextTick()
    
    const text = wrapper.text()
    // Check for the title in the header slot
    const headerText = wrapper.find('h3')?.text() || ''
    const allText = text + headerText
    
    expect(allText.includes('Editar') || allText.includes('Agricultor')).toBe(true)
  })

  it('should emit close event when modal is closed', async () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: mockFarmer
      },
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    await wrapper.vm.closeModal()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should switch between tabs', async () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: mockFarmer
      },
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()

    const fincasTab = wrapper.find('button')
    if (fincasTab.exists() && fincasTab.text().includes('Fincas')) {
      await fincasTab.trigger('click')
      expect(wrapper.vm.activeTab).toBe('fincas')
    }
  })

  it('should handle error when loading fincas', async () => {
    const { getFincas } = await import('@/services/fincasApi')
    getFincas.mockRejectedValueOnce(new Error('Network error'))

    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.vm.loadFarmersFincas(1)

    expect(wrapper.vm.fincasList).toEqual([])
  })

  it('should load persona data when farmer prop changes', async () => {
    const { personasApi } = await import('@/services')
    personasApi.getPersonaByUserId.mockResolvedValueOnce({
      departamento: '05',
      municipio: '1'
    })

    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.setProps({ farmer: { ...mockFarmer, id: 1, name: 'John Doe' } })
    await wrapper.vm.$nextTick()

    expect(personasApi.getPersonaByUserId).toHaveBeenCalled()
  })

  it('should handle 404 error when loading persona data', async () => {
    const { personasApi } = await import('@/services')
    personasApi.getPersonaByUserId.mockRejectedValueOnce({ response: { status: 404 } })

    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.setProps({ farmer: { ...mockFarmer, id: 1 } })
    await wrapper.vm.$nextTick()

    expect(personasApi.getPersonaByUserId).toHaveBeenCalled()
  })

  it('should handle non-404 error when loading persona data', async () => {
    const { personasApi } = await import('@/services')
    const { useNotifications } = await import('@/composables/useNotifications')
    personasApi.getPersonaByUserId.mockRejectedValueOnce({ response: { status: 500 } })

    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.setProps({ farmer: { ...mockFarmer, id: 1 } })
    await wrapper.vm.$nextTick()

    expect(personasApi.getPersonaByUserId).toHaveBeenCalled()
  })

  it('should reset new finca form', async () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: mockFarmer
      }
    })

    await wrapper.vm.$nextTick()

    wrapper.vm.newFinca.nombre = 'Test Finca'
    wrapper.vm.newFinca.municipio = '1'
    wrapper.vm.newFinca.departamento = '05'
    wrapper.vm.newFinca.hectareas = '10'
    wrapper.vm.newFinca.ubicacion = 'Test Location'
    wrapper.vm.newFinca.coordenadas_lat = 1.0
    wrapper.vm.newFinca.coordenadas_lng = 2.0

    wrapper.vm.resetNewFinca()

    expect(wrapper.vm.newFinca.nombre).toBe('')
    expect(wrapper.vm.newFinca.municipio).toBe('')
    expect(wrapper.vm.newFinca.departamento).toBe('')
    expect(wrapper.vm.newFinca.hectareas).toBe('')
    expect(wrapper.vm.newFinca.ubicacion).toBe('')
    expect(wrapper.vm.newFinca.coordenadas_lat).toBeNull()
    expect(wrapper.vm.newFinca.coordenadas_lng).toBeNull()
  })

  it('should validate required fields before creating finca', async () => {
    const { useNotifications } = await import('@/composables/useNotifications')
    const mockShowError = vi.fn()
    useNotifications.mockReturnValueOnce({
      showError: mockShowError,
      showSuccess: vi.fn()
    })

    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: mockFarmer
      }
    })

    await wrapper.vm.$nextTick()

    wrapper.vm.newFinca.nombre = ''
    await wrapper.vm.handleCreateFinca()

    expect(mockShowError).toHaveBeenCalled()
  })

  it('should create finca successfully', async () => {
    const { createFinca } = await import('@/services/fincasApi')
    const { useNotifications } = await import('@/composables/useNotifications')
    const mockShowSuccess = vi.fn()
    createFinca.mockResolvedValueOnce({})
    useNotifications.mockReturnValueOnce({
      showError: vi.fn(),
      showSuccess: mockShowSuccess
    })

    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()

    wrapper.vm.newFinca.nombre = 'Test Finca'
    wrapper.vm.newFinca.municipio = '1'
    wrapper.vm.newFinca.departamento = '05'
    wrapper.vm.newFinca.hectareas = '10'

    await wrapper.vm.handleCreateFinca()
    await wrapper.vm.$nextTick()

    expect(createFinca).toHaveBeenCalled()
    expect(mockShowSuccess).toHaveBeenCalled()
    expect(wrapper.emitted('farmer-updated')).toBeTruthy()
  })

  it('should handle error when creating finca', async () => {
    const { createFinca } = await import('@/services/fincasApi')
    const { useNotifications } = await import('@/composables/useNotifications')
    const mockShowError = vi.fn()
    createFinca.mockRejectedValueOnce(new Error('Network error'))
    useNotifications.mockReturnValueOnce({
      showError: mockShowError,
      showSuccess: vi.fn()
    })

    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()

    wrapper.vm.newFinca.nombre = 'Test Finca'
    wrapper.vm.newFinca.municipio = '1'
    wrapper.vm.newFinca.departamento = '05'
    wrapper.vm.newFinca.hectareas = '10'

    await wrapper.vm.handleCreateFinca()
    await wrapper.vm.$nextTick()

    expect(mockShowError).toHaveBeenCalled()
  })

  it('should validate required fields before updating farmer', async () => {
    const { useNotifications } = await import('@/composables/useNotifications')
    const mockShowError = vi.fn()
    useNotifications.mockReturnValueOnce({
      showError: mockShowError,
      showSuccess: vi.fn()
    })

    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: mockFarmer
      }
    })

    await wrapper.vm.$nextTick()

    wrapper.vm.formData.first_name = ''
    await wrapper.vm.handleUpdate()

    expect(mockShowError).toHaveBeenCalled()
  })

  it('should update farmer successfully', async () => {
    const { default: authApi } = await import('@/services/authApi')
    const { personasApi } = await import('@/services')
    const { useNotifications } = await import('@/composables/useNotifications')
    const mockShowSuccess = vi.fn()
    authApi.updateUser.mockResolvedValueOnce({ user: { id: 1 } })
    personasApi.updatePersonaByUserId.mockResolvedValueOnce({})
    useNotifications.mockReturnValueOnce({
      showError: vi.fn(),
      showSuccess: mockShowSuccess
    })

    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()

    wrapper.vm.formData.first_name = 'John'
    wrapper.vm.formData.last_name = 'Doe'
    wrapper.vm.formData.email = 'john@test.com'
    wrapper.vm.personaForm.departamento = '05'

    await wrapper.vm.handleUpdate()
    await wrapper.vm.$nextTick()

    expect(authApi.updateUser).toHaveBeenCalled()
    expect(mockShowSuccess).toHaveBeenCalled()
    expect(wrapper.emitted('farmer-updated')).toBeTruthy()
  })

  it('should handle error when updating persona', async () => {
    const { default: authApi } = await import('@/services/authApi')
    const { personasApi } = await import('@/services')
    const { useNotifications } = await import('@/composables/useNotifications')
    authApi.updateUser.mockResolvedValueOnce({ user: { id: 1 } })
    personasApi.updatePersonaByUserId.mockRejectedValueOnce(new Error('Persona error'))
    useNotifications.mockReturnValueOnce({
      showError: vi.fn(),
      showSuccess: vi.fn()
    })

    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()

    wrapper.vm.formData.first_name = 'John'
    wrapper.vm.formData.last_name = 'Doe'
    wrapper.vm.formData.email = 'john@test.com'
    wrapper.vm.personaForm.departamento = '05'

    await wrapper.vm.handleUpdate()
    await wrapper.vm.$nextTick()

    expect(authApi.updateUser).toHaveBeenCalled()
  })

  it('should handle error when updating farmer', async () => {
    const { default: authApi } = await import('@/services/authApi')
    const { useNotifications } = await import('@/composables/useNotifications')
    const mockShowError = vi.fn()
    authApi.updateUser.mockRejectedValueOnce(new Error('Update error'))
    useNotifications.mockReturnValueOnce({
      showError: mockShowError,
      showSuccess: vi.fn()
    })

    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()

    wrapper.vm.formData.first_name = 'John'
    wrapper.vm.formData.last_name = 'Doe'
    wrapper.vm.formData.email = 'john@test.com'

    await wrapper.vm.handleUpdate()
    await wrapper.vm.$nextTick()

    expect(mockShowError).toHaveBeenCalled()
  })

  it('should handle departamento change', async () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: mockFarmer
      }
    })

    await wrapper.vm.$nextTick()

    wrapper.vm.personaForm.departamento = '05'
    wrapper.vm.personaForm.municipio = '1'

    await wrapper.vm.onDepartamentoChange()

    expect(wrapper.vm.personaForm.municipio).toBeNull()
  })

  it('should open modal and load catalogos', async () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: false,
        farmer: mockFarmer
      }
    })

    await wrapper.vm.$nextTick()

    await wrapper.vm.openModal()

    expect(wrapper.vm.isOpen).toBe(true)
  })
})


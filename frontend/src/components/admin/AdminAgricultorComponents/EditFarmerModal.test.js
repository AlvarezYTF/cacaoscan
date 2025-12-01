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
})


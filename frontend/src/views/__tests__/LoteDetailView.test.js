import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LoteDetailView from '../LoteDetailView.vue'

// Mock stores
const mockAuthStore = {
  user: { id: 1, role: 'farmer' },
  userRole: 'farmer',
  accessToken: 'mock-token',
  logout: vi.fn()
}

const mockNotificationStore = {
  showNotification: vi.fn()
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => mockNotificationStore
}))

// Mock api service - define mock inside factory to avoid hoisting issues
vi.mock('@/services/api', () => {
  const mockApi = {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn()
  }
  return {
    default: mockApi
  }
})

// Import api after mock to access the mocked instance
import api from '@/services/api.js'

// Create mockApi reference for easier access in tests
const mockApi = api

// Mock sweetalert2 - define mock inside factory to avoid hoisting issues
vi.mock('sweetalert2', () => {
  const mockSwal = {
    fire: vi.fn().mockResolvedValue({ isConfirmed: false })
  }
  return {
    default: mockSwal
  }
})

// Import Swal after mock to use in tests
import Swal from 'sweetalert2'

// Mock vue-router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn()
}

const mockRoute = {
  path: '/lotes/1',
  name: 'LoteDetail',
  params: { id: '1' },
  query: {},
  meta: {}
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter,
    useRoute: () => mockRoute
  }
})

describe('LoteDetailView', () => {
  let wrapper

  const mockLote = {
    id: 1,
    identificador: 'LOTE-001',
    variedad: 'Criollo',
    area_hectareas: 5.5,
    fecha_plantacion: '2024-01-15',
    fecha_registro: '2024-01-10',
    estado: 'activo',
    estado_display: 'Activo',
    descripcion: 'Lote de prueba',
    finca: 1,
    total_analisis: 10,
    analisis_exitosos: 8,
    promedio_calidad: 85,
    ultimo_analisis: '2024-03-15'
  }

  const mockFinca = {
    id: 1,
    nombre: 'Finca Test',
    agricultor: 1
  }

  const mockAnalisisRecientes = [
    {
      id: 1,
      fecha_analisis: '2024-03-15',
      tipo_analisis: 'Calidad',
      calidad: 90
    },
    {
      id: 2,
      fecha_analisis: '2024-03-10',
      tipo_analisis: 'Calidad',
      calidad: 75
    },
    {
      id: 3,
      fecha_analisis: '2024-03-05',
      tipo_analisis: 'Calidad',
      calidad: 55
    }
  ]

  const createWrapper = (options = {}) => {
    return mount(LoteDetailView, {
      global: {
        stubs: {
          'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
        },
        plugins: [createPinia()]
      },
      ...options
    })
  }

  // Helper function to wait for component updates with shorter timeout
  const waitForUpdate = async (ms = 50) => {
    await new Promise(resolve => setTimeout(resolve, ms))
    await flushPromises()
  }

  beforeEach(() => {
    // Ensure real timers are being used at the start of each test
    if (vi.isFakeTimers()) {
      vi.useRealTimers()
    }
    
    setActivePinia(createPinia())
    vi.clearAllMocks()
    
    // Reset route mock
    mockRoute.params = { id: '1' }
    mockRoute.query = {}
    mockRoute.path = '/lotes/1'
    mockRoute.name = 'LoteDetail'
    
    // Reset auth store
    mockAuthStore.user = { id: 1, role: 'farmer' }
    mockAuthStore.userRole = 'farmer'
    mockAuthStore.logout.mockClear()
    
    // Setup default api mocks - reset all mocks first
    mockApi.get.mockReset()
    mockApi.post.mockReset()
    mockApi.delete.mockReset()
    
    mockApi.get.mockImplementation((url) => {
      if (url.includes('/lotes/1/') && !url.includes('/analisis/')) {
        return Promise.resolve({ data: mockLote })
      }
      if (url.includes('/lotes/1/analisis/')) {
        return Promise.resolve({ data: { results: mockAnalisisRecientes } })
      }
      if (url.includes('/api/v1/fincas/1/')) {
        return Promise.resolve({ data: mockFinca })
      }
      return Promise.reject(new Error('Not found'))
    })
    
    mockApi.post.mockResolvedValue({ data: { id: 1 } })
    mockApi.delete.mockResolvedValue({ data: {} })
    
    // Setup default Swal mock
    Swal.fire.mockReset()
    Swal.fire.mockResolvedValue({ isConfirmed: false })
  })

  afterEach(() => {
    // Ensure fake timers are cleared if they were used
    if (vi.isFakeTimers()) {
      vi.useRealTimers()
    }
    
    if (wrapper) {
      try {
        wrapper.unmount()
        wrapper = null
      } catch (e) {
        // Log error for debugging but continue cleanup
        wrapper = null
      }
    }
    
    vi.clearAllMocks()
  })

  it('should render component', () => {
    wrapper = createWrapper()
    expect(wrapper.exists()).toBe(true)
  })

  it('should display loading state initially', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.loading).toBe(true)
    expect(wrapper.text()).toContain('Cargando')
  })

  it('should load lote data on mount', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 50))
    await wrapper.vm.$nextTick()
    
    expect(mockApi.get).toHaveBeenCalledWith('/lotes/1/')
  }, 5000)

  it('should load finca data when lote has finca', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/fincas/1/')
  }, 5000)

  it('should load analisis recientes on mount', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(mockApi.get).toHaveBeenCalledWith('/lotes/1/analisis/')
  }, 5000)

  it('should display lote information when loaded', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).toContain('LOTE-001')
    expect(wrapper.text()).toContain('Criollo')
    expect(wrapper.text()).toContain('5.5 hectáreas')
  }, 5000)

  it('should display breadcrumb navigation', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const breadcrumb = wrapper.find('nav[aria-label="breadcrumb"]')
    expect(breadcrumb.exists()).toBe(true)
    expect(wrapper.text()).toContain('Fincas')
    expect(wrapper.text()).toContain('Lotes')
  }, 5000)

  it('should display error state when loading fails', async () => {
    mockApi.get.mockRejectedValueOnce(new Error('Network error'))
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(100)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.error).toBeTruthy()
    expect(wrapper.text()).toContain('Error')
  })

  it('should handle 404 error and redirect', async () => {
    const error404 = {
      response: {
        status: 404,
        data: { detail: 'Not found' }
      }
    }
    
    mockApi.get.mockRejectedValueOnce(error404)
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(100)
    await wrapper.vm.$nextTick()
    
    expect(mockRouter.push).toHaveBeenCalledWith({ name: 'Fincas' })
  })

  it('should handle 403 error and redirect', async () => {
    const error403 = {
      response: {
        status: 403,
        data: { detail: 'Forbidden' }
      }
    }
    
    mockApi.get.mockRejectedValueOnce(error403)
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(100)
    await wrapper.vm.$nextTick()
    
    expect(mockRouter.push).toHaveBeenCalledWith({ name: 'Fincas' })
  })

  it('should handle 401 error and logout', async () => {
    const error401 = {
      response: {
        status: 401,
        data: { detail: 'Unauthorized' }
      }
    }
    
    mockApi.get.mockRejectedValueOnce(error401)
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Wait for error handling to complete (component uses setTimeout with 2000ms)
    await new Promise(resolve => setTimeout(resolve, 2100))
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    expect(mockAuthStore.logout).toHaveBeenCalledWith(false)
  }, 5000)

  it('should display estadísticas del lote', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).toContain('Estadísticas del Lote')
    expect(wrapper.text()).toContain('10')
    expect(wrapper.text()).toContain('Análisis Realizados')
    expect(wrapper.text()).toContain('8')
    expect(wrapper.text()).toContain('Análisis Exitosos')
    expect(wrapper.text()).toContain('85%')
    expect(wrapper.text()).toContain('Calidad Promedio')
  }, 5000)

  it('should display estado badge with correct color', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const badge = wrapper.find('.badge')
    expect(badge.exists()).toBe(true)
    expect(badge.classes()).toContain('bg-success')
    expect(badge.text()).toContain('Activo')
  }, 5000)

  it('should display estado badge as warning for inactivo', async () => {
    const loteInactivo = { ...mockLote, estado: 'inactivo', estado_display: 'Inactivo' }
    mockApi.get.mockImplementationOnce((url) => {
      if (url.includes('/lotes/1/') && !url.includes('/analisis/')) {
        return Promise.resolve({ data: loteInactivo })
      }
      if (url.includes('/lotes/1/analisis/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url.includes('/api/v1/fincas/1/')) {
        return Promise.resolve({ data: mockFinca })
      }
      return Promise.reject(new Error('Not found'))
    })
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const badge = wrapper.find('.badge')
    expect(badge.classes()).toContain('bg-warning')
  }, 5000)

  it('should display estado badge as info for cosechado', async () => {
    const loteCosechado = { ...mockLote, estado: 'cosechado', estado_display: 'Cosechado' }
    mockApi.get.mockImplementationOnce((url) => {
      if (url.includes('/lotes/1/') && !url.includes('/analisis/')) {
        return Promise.resolve({ data: loteCosechado })
      }
      if (url.includes('/lotes/1/analisis/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url.includes('/api/v1/fincas/1/')) {
        return Promise.resolve({ data: mockFinca })
      }
      return Promise.reject(new Error('Not found'))
    })
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const badge = wrapper.find('.badge')
    expect(badge.classes()).toContain('bg-info')
  }, 5000)

  it('should show edit button when canEdit is true', async () => {
    mockAuthStore.userRole = 'admin'
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const editButton = wrapper.find('button.btn-outline-primary')
    expect(editButton.exists()).toBe(true)
    expect(editButton.text()).toContain('Editar')
  }, 5000)

  it('should hide edit button when canEdit is false', async () => {
    // Set user to different ID before mounting
    mockAuthStore.userRole = 'farmer'
    mockAuthStore.user = { id: 2, role: 'farmer' }
    const fincaOtroUsuario = { ...mockFinca, agricultor: 1 }
    mockApi.get.mockImplementation((url) => {
      if (url.includes('/lotes/1/') && !url.includes('/analisis/')) {
        return Promise.resolve({ data: mockLote })
      }
      if (url.includes('/lotes/1/analisis/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url.includes('/api/v1/fincas/1/')) {
        return Promise.resolve({ data: fincaOtroUsuario })
      }
      return Promise.reject(new Error('Not found'))
    })
    
    wrapper = createWrapper()
    
    // Wait for all async operations: loadLote, loadFinca, loadAnalisisRecientes
    await wrapper.vm.$nextTick()
    await flushPromises()
    await wrapper.vm.$nextTick()
    await flushPromises()
    await wrapper.vm.$nextTick()
    
    // Verify canEdit is false (user.id=2, finca.agricultor=1)
    expect(wrapper.vm.canEdit).toBe(false)
    
    // Search for edit button specifically by looking for button containing "Editar" text
    const allButtons = wrapper.findAll('button.btn-outline-primary')
    const editButton = allButtons.find(button => button.text().includes('Editar'))
    expect(editButton).toBeUndefined()
  }, 5000)

  it('should show delete button when canDelete is true', async () => {
    mockAuthStore.userRole = 'admin'
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const deleteButton = wrapper.find('button.btn-outline-danger')
    expect(deleteButton.exists()).toBe(true)
    expect(deleteButton.text()).toContain('Eliminar')
  }, 5000)

  it('should hide delete button when canDelete is false', async () => {
    mockAuthStore.userRole = 'farmer'
    mockAuthStore.user.id = 2
    const fincaOtroUsuario = { ...mockFinca, agricultor: 1 }
    mockApi.get.mockImplementation((url) => {
      if (url.includes('/lotes/1/') && !url.includes('/analisis/')) {
        return Promise.resolve({ data: mockLote })
      }
      if (url.includes('/lotes/1/analisis/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url.includes('/api/v1/fincas/1/')) {
        return Promise.resolve({ data: fincaOtroUsuario })
      }
      return Promise.reject(new Error('Not found'))
    })
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const deleteButton = wrapper.find('button.btn-outline-danger')
    expect(deleteButton.exists()).toBe(false)
  }, 5000)

  it('should navigate to edit page when edit button is clicked', async () => {
    mockAuthStore.userRole = 'admin'
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const editButton = wrapper.find('button.btn-outline-primary')
    await editButton.trigger('click')
    await wrapper.vm.$nextTick()
    
    expect(mockRouter.push).toHaveBeenCalledWith('/lotes/1/edit')
  }, 5000)

  it('should navigate to analyze page when analyze button is clicked', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const analyzeButton = wrapper.find('button.btn-success')
    await analyzeButton.trigger('click')
    await wrapper.vm.$nextTick()
    
    expect(mockRouter.push).toHaveBeenCalledWith('/analisis?lote=1')
  }, 5000)

  it('should navigate to analisis page when view analisis button is clicked', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const viewButton = wrapper.find('button.btn-outline-info')
    await viewButton.trigger('click')
    await wrapper.vm.$nextTick()
    
    expect(mockRouter.push).toHaveBeenCalledWith('/lotes/1/analisis')
  }, 5000)

  it('should hide view analisis button when no analisis exist', async () => {
    const loteSinAnalisis = { ...mockLote, total_analisis: 0 }
    mockApi.get.mockImplementation((url) => {
      if (url.includes('/lotes/1/') && !url.includes('/analisis/')) {
        return Promise.resolve({ data: loteSinAnalisis })
      }
      if (url.includes('/lotes/1/analisis/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url.includes('/api/v1/fincas/1/')) {
        return Promise.resolve({ data: mockFinca })
      }
      return Promise.reject(new Error('Not found'))
    })
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const viewButton = wrapper.find('button.btn-outline-info')
    expect(viewButton.exists()).toBe(false)
  }, 5000)

  it('should generate report when generate report button is clicked', async () => {
    Swal.fire.mockReset()
    Swal.fire
      .mockResolvedValueOnce({}) // Loading dialog (first Swal.fire call)
      .mockResolvedValueOnce({}) // Success dialog (second Swal.fire call)
    
    api.post.mockResolvedValueOnce({ data: { id: 1 } })
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(100)
    await wrapper.vm.$nextTick()
    
    // Call generateReport method directly
    await wrapper.vm.generateReport()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(100)
    await wrapper.vm.$nextTick()
    
    expect(Swal.fire).toHaveBeenCalled()
    expect(api.post).toHaveBeenCalledWith('/reportes/', expect.objectContaining({
      tipo_reporte: 'lote',
      formato: 'pdf',
      titulo: 'Reporte de Lote: LOTE-001',
      parametros: {
        lote_id: 1
      }
    }))
  }, 5000)

  it('should handle report generation error', async () => {
    Swal.fire.mockReset()
    Swal.fire
      .mockResolvedValueOnce({}) // Loading dialog (first Swal.fire call)
      .mockResolvedValueOnce({}) // Error dialog (catch block Swal.fire call)
    api.post.mockRejectedValueOnce(new Error('Report error'))
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(100)
    await wrapper.vm.$nextTick()
    
    // Call generateReport method directly
    await wrapper.vm.generateReport()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(100)
    await wrapper.vm.$nextTick()
    
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Error',
        text: 'No se pudo generar el reporte',
        icon: 'error'
      })
    )
  }, 5000)

  it('should delete lote when delete button is clicked and confirmed', async () => {
    mockAuthStore.userRole = 'admin'
    Swal.fire
      .mockResolvedValueOnce({ isConfirmed: true }) // Confirmation dialog
      .mockResolvedValueOnce({ isConfirmed: false }) // Success dialog
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const deleteButton = wrapper.find('button.btn-outline-danger')
    await deleteButton.trigger('click')
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        title: '¿Eliminar Lote?',
        text: 'Esta acción no se puede deshacer',
        icon: 'warning'
      })
    )
    expect(mockApi.delete).toHaveBeenCalledWith('/lotes/1/')
    expect(mockRouter.push).toHaveBeenCalledWith('/fincas/1/lotes')
  }, 5000)

  it('should not delete lote when delete is cancelled', async () => {
    mockAuthStore.userRole = 'admin'
    Swal.fire.mockResolvedValueOnce({ isConfirmed: false })
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const deleteButton = wrapper.find('button.btn-outline-danger')
    await deleteButton.trigger('click')
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    expect(mockApi.delete).not.toHaveBeenCalled()
  }, 5000)

  it('should handle delete error', async () => {
    mockAuthStore.userRole = 'admin'
    Swal.fire
      .mockResolvedValueOnce({ isConfirmed: true })
    mockApi.delete.mockRejectedValueOnce(new Error('Delete error'))
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const deleteButton = wrapper.find('button.btn-outline-danger')
    await deleteButton.trigger('click')
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Error',
        text: 'No se pudo eliminar el lote',
        icon: 'error'
      })
    )
  }, 5000)

  it('should display analisis recientes', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).toContain('Análisis Recientes')
    expect(wrapper.text()).toContain('Calidad')
  }, 5000)

  it('should display calidad badge with correct color for high quality', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const badges = wrapper.findAll('.badge')
    const calidadBadge = badges.find(badge => badge.text().includes('90'))
    expect(calidadBadge.exists()).toBe(true)
    expect(calidadBadge.classes()).toContain('bg-success')
  }, 5000)

  it('should display calidad badge with warning color for medium quality', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const badges = wrapper.findAll('.badge')
    const calidadBadge = badges.find(badge => badge.text().includes('75'))
    expect(calidadBadge.exists()).toBe(true)
    expect(calidadBadge.classes()).toContain('bg-warning')
  }, 5000)

  it('should display calidad badge with danger color for low quality', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    const badges = wrapper.findAll('.badge')
    const calidadBadge = badges.find(badge => badge.text().includes('55'))
    expect(calidadBadge.exists()).toBe(true)
    expect(calidadBadge.classes()).toContain('bg-danger')
  }, 5000)

  it('should hide analisis recientes section when no analisis exist', async () => {
    mockApi.get.mockImplementation((url) => {
      if (url.includes('/lotes/1/') && !url.includes('/analisis/')) {
        return Promise.resolve({ data: mockLote })
      }
      if (url.includes('/lotes/1/analisis/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url.includes('/api/v1/fincas/1/')) {
        return Promise.resolve({ data: mockFinca })
      }
      return Promise.reject(new Error('Not found'))
    })
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).not.toContain('Análisis Recientes')
  }, 5000)

  it('should format date correctly', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    
    const formattedDate = wrapper.vm.formatDate('2024-01-15')
    expect(formattedDate).toBeTruthy()
    expect(typeof formattedDate).toBe('string')
  })

  it('should display finca link when finca is loaded', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).toContain('Finca Test')
  }, 5000)

  it('should display descripcion when available', async () => {
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).toContain('Lote de prueba')
  }, 5000)

  it('should retry loading when retry button is clicked', async () => {
    mockApi.get.mockRejectedValueOnce(new Error('Network error'))
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(100)
    await wrapper.vm.$nextTick()
    
    // Reset mock to succeed on retry
    mockApi.get.mockResolvedValueOnce({ data: mockLote })
    mockApi.get.mockResolvedValueOnce({ data: { results: [] } })
    mockApi.get.mockResolvedValueOnce({ data: mockFinca })
    
    const retryButton = wrapper.find('button.btn-outline-danger')
    await retryButton.trigger('click')
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(mockApi.get).toHaveBeenCalledWith('/lotes/1/')
  }, 5000)

  it('should handle network error', async () => {
    const networkError = {
      request: {},
      message: 'Network Error'
    }
    
    mockApi.get.mockRejectedValueOnce(networkError)
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(100)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.error).toContain('No se pudo conectar al servidor')
  }, 5000)

  it('should handle unknown error', async () => {
    const unknownError = {
      message: 'Unknown error'
    }
    
    mockApi.get.mockRejectedValueOnce(unknownError)
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(100)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.error).toBe('Unknown error')
  }, 5000)

  it('should allow farmer to edit own finca lote', async () => {
    mockAuthStore.userRole = 'farmer'
    mockAuthStore.user.id = 1
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.canEdit).toBe(true)
  }, 5000)

  it('should not allow farmer to edit other finca lote', async () => {
    mockAuthStore.userRole = 'farmer'
    mockAuthStore.user.id = 2
    const fincaOtroUsuario = { ...mockFinca, agricultor: 1 }
    mockApi.get.mockImplementation((url) => {
      if (url.includes('/lotes/1/') && !url.includes('/analisis/')) {
        return Promise.resolve({ data: mockLote })
      }
      if (url.includes('/lotes/1/analisis/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url.includes('/api/v1/fincas/1/')) {
        return Promise.resolve({ data: fincaOtroUsuario })
      }
      return Promise.reject(new Error('Not found'))
    })
    
    wrapper = createWrapper()
    
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitForUpdate(50)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.canEdit).toBe(false)
  }, 5000)
})


import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import FincaLotesView from '../FincaLotesView.vue'

// Mock stores
const mockAuthStore = {
  user: { id: 1, role: 'farmer' },
  userRole: 'farmer',
  accessToken: 'mock-token'
}

const mockNotificationStore = {
  showSuccess: vi.fn(),
  showError: vi.fn()
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => mockNotificationStore
}))

// Mock usePagination composable
const createMockPagination = () => ({
  currentPage: { value: 1 },
  totalPages: { value: 1 },
  itemsPerPage: { value: 10 },
  totalItems: { value: 0 },
  visiblePages: { value: [1] },
  hasNextPage: { value: false },
  hasPreviousPage: { value: false },
  goToPage: vi.fn(),
  updatePagination: vi.fn(),
  updateFromApiResponse: vi.fn(),
  setTotalItems: vi.fn(),
  reset: vi.fn()
})

const mockPagination = createMockPagination()

vi.mock('@/composables/usePagination', () => ({
  usePagination: vi.fn((...args) => {
    // Handle both usePagination(1, 10) and usePagination({ initialPage: 1, initialItemsPerPage: 10 })
    if (typeof args[0] === 'number') {
      mockPagination.currentPage.value = args[0] || 1
      mockPagination.itemsPerPage.value = args[1] || 10
    } else if (args[0] && typeof args[0] === 'object') {
      mockPagination.currentPage.value = args[0].initialPage || 1
      mockPagination.itemsPerPage.value = args[0].initialItemsPerPage || 10
    }
    return mockPagination
  })
}))

// Mock fetch globally
globalThis.fetch = vi.fn()

// Mock vue-router composables
const mockRoute = {
  params: { id: '1' },
  query: {},
  path: '/fincas/1/lotes',
  name: 'FincaLotes'
}

const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn()
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => mockRoute,
    useRouter: () => mockRouter
  }
})

describe('FincaLotesView', () => {
  let wrapper

  const mockFinca = {
    id: 1,
    nombre: 'Finca Test',
    agricultor: 1
  }

  const mockLotes = [
    {
      id: 1,
      identificador: 'LOTE-001',
      variedad: 'Criollo',
      area_hectareas: 5.5,
      estado: 'activo',
      estado_display: 'Activo',
      fecha_plantacion: '2024-01-15',
      total_analisis: 3
    },
    {
      id: 2,
      identificador: 'LOTE-002',
      variedad: 'Forastero',
      area_hectareas: 3.2,
      estado: 'cosechado',
      estado_display: 'Cosechado',
      fecha_plantacion: '2023-06-20',
      total_analisis: 0
    },
    {
      id: 3,
      identificador: 'LOTE-003',
      variedad: 'Trinitario',
      area_hectareas: 7.8,
      estado: 'inactivo',
      estado_display: 'Inactivo',
      fecha_plantacion: '2022-03-10',
      total_analisis: 1
    }
  ]

  const createWrapper = (options = {}) => {
    return mount(FincaLotesView, {
      global: {
        stubs: {
          'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
        },
        mocks: {
          $route: mockRoute,
          $router: mockRouter
        }
      },
      ...options
    })
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset route mock
    mockRoute.params = { id: '1' }
    mockRoute.query = {}
    mockRoute.path = '/fincas/1/lotes'
    mockRoute.name = 'FincaLotes'
    mockRouter.push.mockClear()
    mockRouter.replace.mockClear()
    // Reset pagination mock
    Object.assign(mockPagination, createMockPagination())
    mockPagination.currentPage.value = 1
    mockPagination.totalPages.value = 1
    mockPagination.itemsPerPage.value = 10
    mockPagination.totalItems.value = 0
    mockPagination.visiblePages.value = [1]
    mockPagination.goToPage.mockClear()
    mockPagination.updatePagination.mockClear()

    // Setup default fetch mocks
    globalThis.fetch.mockImplementation((url) => {
      if (url.includes('/fincas/1/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockFinca)
        })
      }
      if (url.includes('/fincas/1/lotes/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ results: mockLotes })
        })
      }
      return Promise.reject(new Error('Not found'))
    })
  })

  afterEach(async () => {
    if (wrapper) {
      try {
        await wrapper.unmount()
        // Force cleanup of Vue instance
        wrapper = null
      } catch {
        // Ignore unmount errors
        wrapper = null
      }
    }
    // Wait longer for any pending operations to complete and ensure Vue instance is fully cleaned up
    // This helps prevent router conflicts between tests
    await new Promise(resolve => setTimeout(resolve, 100))
    // Clear all mocks to prevent state leakage
    vi.clearAllMocks()
    // Reset auth store to default values
    mockAuthStore.userRole = 'farmer'
    mockAuthStore.user.id = 1
  })

  it('should render component', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    expect(wrapper.exists()).toBe(true)
  })

  it('should display breadcrumb navigation', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    const breadcrumb = wrapper.find('nav[aria-label="breadcrumb"]')
    expect(breadcrumb.exists()).toBe(true)
    expect(wrapper.text()).toContain('Fincas')
    expect(wrapper.text()).toContain('Lotes')
  })

  it('should display loading state initially', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    
    // Component should be loading initially
    expect(wrapper.vm.loading).toBe(true)
  })

  it('should load finca data on mount', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/fincas/1/'),
      expect.any(Object)
    )
  })

  it('should load lotes data on mount', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/fincas/1/lotes/'),
      expect.any(Object)
    )
  })

  it('should display error state when loading fails', async () => {
    // Override the default mock to reject for loadLotes call
    globalThis.fetch.mockImplementation((url) => {
      if (url.includes('/fincas/1/') && !url.includes('/lotes/')) {
        // Allow loadFinca to succeed
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockFinca)
        })
      }
      if (url.includes('/fincas/1/lotes/')) {
        // Reject for loadLotes
        return Promise.reject(new Error('Network error'))
      }
      return Promise.reject(new Error('Not found'))
    })

    wrapper = createWrapper()

    // Wait for onMounted to call loadLotes and handle the error
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 300))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.error).toBeTruthy()
    expect(wrapper.vm.error).toBe('Network error')
  })

  it('should display finca name in header', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.finca = mockFinca
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Finca Test')
  })

  it('should display "Finca" when finca name is not available', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Finca')
  })

  it('should show create button when canCreate is true', async () => {
    mockAuthStore.userRole = 'admin'
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.finca = mockFinca
    await wrapper.vm.$nextTick()

    const createButton = wrapper.find('button.btn-primary')
    expect(createButton.exists()).toBe(true)
    expect(createButton.text()).toContain('Nuevo Lote')
  })

  it('should hide create button when canCreate is false', async () => {
    mockAuthStore.userRole = 'farmer'
    mockAuthStore.user.id = 2 // Different user
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.finca = { ...mockFinca, agricultor: 1 }
    await wrapper.vm.$nextTick()

    const createButton = wrapper.find('button.btn-primary')
    expect(createButton.exists()).toBe(false)
  })

  it('should display statistics correctly', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    // Wait for loadLotes to complete (the default mock in beforeEach already returns mockLotes)
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()
    // Ensure lotes are set
    if (wrapper.vm.lotes.length === 0) {
      // If lotes weren't loaded, set them manually for the test
      wrapper.vm.lotes = [...mockLotes]
      await wrapper.vm.$nextTick()
    }

    expect(wrapper.vm.stats.total).toBe(3)
    expect(wrapper.vm.stats.activos).toBe(1)
    expect(wrapper.vm.stats.cosechados).toBe(1)
    expect(wrapper.vm.stats.analisis).toBe(2) // 2 lotes con total_analisis > 0
  })

  it('should filter lotes by search term', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Set lotes directly - ensure it's set as an array
    if (Array.isArray(wrapper.vm.lotes)) {
      wrapper.vm.lotes.splice(0, wrapper.vm.lotes.length, ...mockLotes)
    } else {
      wrapper.vm.lotes = [...mockLotes]
    }
    wrapper.vm.loading = false
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Verify lotes are set correctly
    expect(Array.isArray(wrapper.vm.lotes)).toBe(true)
    expect(wrapper.vm.lotes.length).toBe(3)
    expect(wrapper.vm.filteredLotes.length).toBe(3) // All lotes should be visible before filtering
    
    // Then set filter and wait for computed to update
    wrapper.vm.filters.search = 'LOTE-001'
    await wrapper.vm.$nextTick()
    await flushPromises()

    expect(wrapper.vm.filteredLotes.length).toBe(1)
    expect(wrapper.vm.filteredLotes[0].identificador).toBe('LOTE-001')
  })

  it('should filter lotes by estado', async () => {
    // Wait to ensure previous router is fully cleaned up
    await new Promise(resolve => setTimeout(resolve, 50))
    
    // The beforeEach already sets up fetch mocks for both finca and lotes
    // Just ensure the lotes mock returns the correct data
    globalThis.fetch.mockImplementation((url) => {
      if (url.includes('/fincas/1/') && !url.includes('/lotes/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockFinca)
        })
      }
      if (url.includes('/fincas/1/lotes/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ results: mockLotes })
        })
      }
      return Promise.reject(new Error('Not found'))
    })
    
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    // Wait for both loadFinca and loadLotes to complete
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()
    
    // Verify lotes are set correctly
    expect(wrapper.vm.lotes.length).toBe(3)
    expect(wrapper.vm.filteredLotes.length).toBe(3) // All lotes should be visible before filtering
    
    // Then set filter and wait for computed to update
    wrapper.vm.filters.estado = 'activo'
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick() // Extra tick to ensure computed updates

    expect(wrapper.vm.filteredLotes.length).toBe(1)
    expect(wrapper.vm.filteredLotes[0].estado).toBe('activo')
  })

  it('should filter lotes by variedad', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Set lotes first
    wrapper.vm.lotes = mockLotes
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Verify lotes are set correctly
    expect(wrapper.vm.lotes).toEqual(mockLotes)
    expect(wrapper.vm.lotes.length).toBe(3)
    
    // Then set filter
    wrapper.vm.filters.variedad = 'Criollo'
    await wrapper.vm.$nextTick()
    await flushPromises()

    expect(wrapper.vm.filteredLotes.length).toBe(1)
    expect(wrapper.vm.filteredLotes[0].variedad).toBe('Criollo')
  })

  it('should clear all filters', async () => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.filters.search = 'test'
    wrapper.vm.filters.estado = 'activo'
    wrapper.vm.filters.variedad = 'Criollo'

    wrapper.vm.clearFilters()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.filters.search).toBe('')
    expect(wrapper.vm.filters.estado).toBe('')
    expect(wrapper.vm.filters.variedad).toBe('')
    expect(mockPagination.goToPage).toHaveBeenCalledWith(1)
  })

  it('should navigate to create lote page', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.fincaId = 1
    wrapper.vm.createLote()
    await wrapper.vm.$nextTick()

    expect(mockRouter.push).toHaveBeenCalledWith('/fincas/1/lotes/new')
  })

  it('should navigate to view lote page', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.viewLote(123)
    await wrapper.vm.$nextTick()

    expect(mockRouter.push).toHaveBeenCalledWith('/lotes/123')
  })

  it('should navigate to edit lote page', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.editLote(456)
    await wrapper.vm.$nextTick()

    expect(mockRouter.push).toHaveBeenCalledWith('/lotes/456/edit')
  })

  it('should navigate to analyze lote page', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.analyzeLote(789)
    await wrapper.vm.$nextTick()

    expect(mockRouter.push).toHaveBeenCalledWith('/analisis/new?lote=789')
  })

  it('should format date correctly', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    const formattedDate = wrapper.vm.formatDate('2024-01-15')
    expect(formattedDate).toBeTruthy()
    expect(typeof formattedDate).toBe('string')
  })

  it('should display lotes in table', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Set lotes first
    wrapper.vm.lotes = mockLotes
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Verify lotes are set correctly
    expect(wrapper.vm.lotes).toEqual(mockLotes)
    expect(wrapper.vm.lotes.length).toBe(3)
    
    // Set loading to false
    wrapper.vm.loading = false
    await wrapper.vm.$nextTick()
    await flushPromises()

    const table = wrapper.find('table')
    expect(table.exists()).toBe(true)
    expect(wrapper.text()).toContain('LOTE-001')
    expect(wrapper.text()).toContain('Criollo')
  })

  it('should display "Sin análisis" when lote has no analysis', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Set lotes first
    const loteSinAnalisis = [{ ...mockLotes[1], total_analisis: 0 }]
    wrapper.vm.lotes = loteSinAnalisis
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Verify lotes are set correctly
    expect(wrapper.vm.lotes).toEqual(loteSinAnalisis)
    expect(wrapper.vm.lotes.length).toBe(1)
    
    // Set loading to false and error to null
    wrapper.vm.loading = false
    wrapper.vm.error = null
    await wrapper.vm.$nextTick()
    await flushPromises()

    expect(wrapper.text()).toContain('Sin análisis')
  })

  it('should display analysis count when lote has analysis', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Set lotes first
    const loteConAnalisis = [{ ...mockLotes[0], total_analisis: 3 }]
    wrapper.vm.lotes = loteConAnalisis
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Verify lotes are set correctly
    expect(wrapper.vm.lotes).toEqual(loteConAnalisis)
    expect(wrapper.vm.lotes.length).toBe(1)
    
    // Set loading to false and error to null
    wrapper.vm.loading = false
    wrapper.vm.error = null
    await wrapper.vm.$nextTick()
    await flushPromises()

    expect(wrapper.text()).toContain('3 análisis')
  })

  it('should show edit button when canEdit is true', async () => {
    mockAuthStore.userRole = 'admin'
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    // Set finca first so canEdit computed can evaluate correctly
    wrapper.vm.finca = mockFinca
    await wrapper.vm.$nextTick()
    
    // Set lotes and update pagination
    wrapper.vm.lotes = mockLotes
    // Manually trigger pagination update since the watch might not fire in tests
    wrapper.vm.pagination.updatePagination({
      page: 1,
      page_size: 10,
      count: mockLotes.length
    })
    wrapper.vm.loading = false
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick() // Extra tick to ensure all computed properties update

    // Verify that displayedLotes has items
    expect(wrapper.vm.displayedLotes.length).toBeGreaterThan(0)
    expect(wrapper.vm.canEdit).toBe(true)
    
    const editButtons = wrapper.findAll('button[title="Editar"]')
    expect(editButtons.length).toBeGreaterThan(0)
  })

  it('should hide edit button when canEdit is false', async () => {
    mockAuthStore.userRole = 'farmer'
    mockAuthStore.user.id = 2
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.lotes = mockLotes
    wrapper.vm.finca = { ...mockFinca, agricultor: 1 }
    wrapper.vm.loading = false
    await wrapper.vm.$nextTick()

    const editButtons = wrapper.findAll('button[title="Editar"]')
    expect(editButtons.length).toBe(0)
  })

  it('should display "No se encontraron lotes" when filteredLotes is empty', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.lotes = []
    wrapper.vm.loading = false
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('No se encontraron lotes')
  })

  it('should extract unique variedades from lotes', async () => {
    // Ensure previous wrapper is unmounted
    if (wrapper) {
      try {
        await wrapper.unmount()
      } catch (error) {
        // Ignore unmount errors - component may already be unmounted
        :', error)
      }
      wrapper = null
      // Wait longer to ensure router is fully cleaned up
      await new Promise(resolve => setTimeout(resolve, 50))
    }
    
    // Mock fetch to return finca and lotes for all calls
    globalThis.fetch.mockImplementation((url) => {
      if (url.includes('/fincas/1/') && !url.includes('/lotes/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockFinca)
        })
      }
      if (url.includes('/fincas/1/lotes/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ results: mockLotes })
        })
      }
      return Promise.reject(new Error('Not found'))
    })
    
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()
    
    // Call loadLotes which will fetch and extract variedades
    await wrapper.vm.loadLotes()
    await wrapper.vm.$nextTick()
    // Wait a bit more for the extraction to complete
    await new Promise(resolve => setTimeout(resolve, 50))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.variedades).toContain('Criollo')
    expect(wrapper.vm.variedades).toContain('Forastero')
    expect(wrapper.vm.variedades).toContain('Trinitario')
  })

  it('should handle pagination correctly', async () => {
    // Ensure previous wrapper is unmounted
    if (wrapper) {
      await wrapper.unmount()
      wrapper = null
      await new Promise(resolve => setTimeout(resolve, 10))
    }
    
    mockPagination.totalPages.value = 3
    mockPagination.visiblePages.value = [1, 2, 3]
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.lotes = Array.from({ length: 25 }, (_, i) => ({
      id: i + 1,
      identificador: `LOTE-${i + 1}`,
      variedad: 'Criollo',
      area_hectareas: 5,
      estado: 'activo',
      estado_display: 'Activo',
      fecha_plantacion: '2024-01-15',
      total_analisis: 0
    }))
    wrapper.vm.loading = false
    await wrapper.vm.$nextTick()

    wrapper.vm.changePage(2)
    await wrapper.vm.$nextTick()

    expect(mockPagination.goToPage).toHaveBeenCalledWith(2)
  })

  it('should not change page if page is out of bounds', async () => {
    mockPagination.totalPages.value = 1
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.changePage(0)
    await wrapper.vm.$nextTick()

    expect(mockPagination.goToPage).not.toHaveBeenCalled()
  })

  it('should retry loading when retry button is clicked', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Set error state and ensure loading is false so error state is shown
    wrapper.vm.error = 'Test error'
    wrapper.vm.loading = false
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 50))
    await wrapper.vm.$nextTick()

    // Find the retry button in the error alert
    const errorAlert = wrapper.find('.alert-danger')
    expect(errorAlert.exists()).toBe(true)
    
    const retryButton = errorAlert.find('button.btn-outline-danger')
    expect(retryButton.exists()).toBe(true)

    // Verify loadLotes exists on the component instance
    expect(wrapper.vm.loadLotes).toBeDefined()
    expect(typeof wrapper.vm.loadLotes).toBe('function')

    // Verify initial state
    expect(wrapper.vm.loading).toBe(false)
    expect(wrapper.vm.error).toBe('Test error')
    
    // Verify the button is actually rendered and has the click handler
    expect(retryButton.element).toBeDefined()
    expect(retryButton.text()).toContain('Intentar nuevamente')
    
    // Mock fetch to track calls - loadLotes calls fetch
    const fetchCallsBeforeClick = globalThis.fetch.mock.calls.length
    
    // Trigger click event on the button
    await retryButton.trigger('click')
    await wrapper.vm.$nextTick()
    await flushPromises()
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Verify that loadLotes was called by checking that fetch was called
    // loadLotes makes a fetch call to `/api/fincas/${fincaId.value}/lotes/`
    expect(globalThis.fetch).toHaveBeenCalled()
    expect(globalThis.fetch.mock.calls.length).toBeGreaterThan(fetchCallsBeforeClick)
    
    // Verify that the fetch call was made to the correct endpoint
    const fetchCalls = globalThis.fetch.mock.calls
    const lotesFetchCall = fetchCalls.find(call => 
      call[0] && typeof call[0] === 'string' && call[0].includes('/lotes/')
    )
    expect(lotesFetchCall).toBeDefined()
  })

  it('should reset to page 1 when filters change', async () => {
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.filters.estado = 'activo'
    await wrapper.vm.$nextTick()

    expect(mockPagination.goToPage).toHaveBeenCalledWith(1)
  })

  it('should handle debounced search', async () => {
    // Ensure previous wrapper is unmounted
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    
    vi.useFakeTimers()
    
    wrapper = createWrapper()

    await wrapper.vm.$nextTick()
    wrapper.vm.debouncedSearch()
    
    expect(mockPagination.goToPage).not.toHaveBeenCalled()
    
    await vi.advanceTimersByTimeAsync(300)
    await wrapper.vm.$nextTick()

    expect(mockPagination.goToPage).toHaveBeenCalledWith(1)
    vi.useRealTimers()
  })
})




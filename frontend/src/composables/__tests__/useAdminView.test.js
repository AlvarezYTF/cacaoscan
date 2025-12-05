/**
 * Unit tests for useAdminView composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAdminView } from '../useAdminView.js'
import { usePagination } from '../usePagination'
import Swal from 'sweetalert2'

// Mock dependencies
const mockRouter = {
  push: vi.fn()
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
  createRouter: vi.fn((options) => mockRouter),
  createWebHistory: vi.fn(() => ({})),
  createWebHashHistory: vi.fn(() => ({})),
  createMemoryHistory: vi.fn(() => ({}))
}))

vi.mock('../usePagination', () => ({
  usePagination: vi.fn(() => ({
    currentPage: { value: 1 },
    totalPages: { value: 1 },
    totalItems: { value: 0 },
    itemsPerPage: { value: 20 },
    goToPage: vi.fn(),
    updateFromApiResponse: vi.fn()
  }))
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn()
  }
}))

describe('useAdminView', () => {
  let adminView

  beforeEach(() => {
    vi.clearAllMocks()
    
    const mockStore = {
      stats: {},
      pagination: { currentPage: 1, totalPages: 1 }
    }
    
    adminView = useAdminView({
      store: mockStore,
      loadData: vi.fn(),
      loadStats: vi.fn()
    })
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(adminView.loading.value).toBe(false)
      expect(adminView.showFilters.value).toBe(false)
      expect(adminView.viewMode.value).toBe('table')
    })
  })

  describe('handleMenuClick', () => {
    it('should navigate to route', () => {
      const menuItem = { route: '/test-route' }
      
      adminView.handleMenuClick(menuItem)
      
      expect(mockRouter.push).toHaveBeenCalledWith('/test-route')
    })
  })

  describe('handleRefresh', () => {
    it('should refresh data', async () => {
      const loadStats = vi.fn().mockResolvedValue()
      const loadData = vi.fn().mockResolvedValue()
      
      const view = useAdminView({
        store: { stats: {} },
        loadStats,
        loadData
      })
      
      await view.handleRefresh()
      
      expect(loadStats).toHaveBeenCalled()
      expect(loadData).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
    })
  })

  describe('applyFilters', () => {
    it('should apply filters', async () => {
      const loadData = vi.fn().mockResolvedValue()
      
      const view = useAdminView({
        store: { stats: {} },
        loadData
      })
      
      await view.applyFilters()
      
      expect(loadData).toHaveBeenCalled()
    })
  })

  describe('clearFilters', () => {
    it('should clear filters and reset to initial', () => {
      adminView.filters.value = { search: 'test' }
      
      adminView.clearFilters()
      
      expect(adminView.filters.value).toEqual({})
    })
  })

  const createAuthStoreMock = (mockAuthStore) => ({
    useAuthStore: () => mockAuthStore
  })

  describe('handleLogout', () => {
    it('should logout and redirect to login', async () => {
      const mockAuthStore = {
        logout: vi.fn().mockResolvedValue()
      }
      
      vi.doMock('@/stores/auth', createAuthStoreMock(mockAuthStore))
      
      await adminView.handleLogout()
      
      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })

    it('should handle logout error', async () => {
      const mockAuthStore = {
        logout: vi.fn().mockRejectedValue(new Error('Logout failed'))
      }
      
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      vi.doMock('@/stores/auth', createAuthStoreMock(mockAuthStore))
      
      await adminView.handleLogout()
      
      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })
  })

  const createAdminViewWithMocks = (loadStats, loadData) => {
    return useAdminView({
      store: { stats: {} },
      loadStats,
      loadData
    })
  }

  describe('loadInitialData', () => {
    it('should load data and stats', async () => {
      const loadStats = vi.fn().mockResolvedValue()
      const loadData = vi.fn().mockResolvedValue()
      
      const view = createAdminViewWithMocks(loadStats, loadData)
      
      await view.loadInitialData()
      
      expect(loadStats).toHaveBeenCalled()
      expect(loadData).toHaveBeenCalledWith({})
      expect(view.loading.value).toBe(false)
    })

    it('should handle load error', async () => {
      const loadStats = vi.fn().mockRejectedValue(new Error('Load failed'))
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      const view = useAdminView({
        store: { stats: {} },
        loadStats
      })
      
      await view.loadInitialData()
      
      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'error',
        title: 'Error',
        text: 'No se pudieron cargar los datos'
      })
      expect(view.loading.value).toBe(false)
      
      consoleError.mockRestore()
    })

    it('should work without loadStats', async () => {
      const loadData = vi.fn().mockResolvedValue()
      
      const view = useAdminView({
        store: { stats: {} },
        loadData
      })
      
      await view.loadInitialData()
      
      expect(loadData).toHaveBeenCalled()
    })

    it('should work without loadData', async () => {
      const loadStats = vi.fn().mockResolvedValue()
      
      const view = useAdminView({
        store: { stats: {} },
        loadStats
      })
      
      await view.loadInitialData()
      
      expect(loadStats).toHaveBeenCalled()
    })
  })

  describe('applyFilters', () => {
    it('should handle apply filters error', async () => {
      const loadData = vi.fn().mockRejectedValue(new Error('Filter failed'))
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      const view = useAdminView({
        store: { stats: {} },
        loadData
      })
      
      await view.applyFilters()
      
      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'error',
        title: 'Error',
        text: 'No se pudieron aplicar los filtros'
      })
      expect(view.loading.value).toBe(false)
      
      consoleError.mockRestore()
    })

    it('should work without loadData', async () => {
      const view = useAdminView({
        store: { stats: {} }
      })
      
      await view.applyFilters()
      
      expect(view.loading.value).toBe(false)
    })
  })

  describe('handlePageChange', () => {
    it('should change page and load data', async () => {
      const loadData = vi.fn().mockResolvedValue()
      const mockPagination = {
        currentPage: { value: 1 },
        totalPages: { value: 1 },
        totalItems: { value: 0 },
        itemsPerPage: { value: 20 },
        goToPage: vi.fn()
      }
      
      usePagination.mockReturnValueOnce(mockPagination)
      
      const view = useAdminView({
        store: { stats: {} },
        loadData
      })
      
      await view.handlePageChange(2)
      
      expect(mockPagination.goToPage).toHaveBeenCalledWith(2)
      expect(loadData).toHaveBeenCalledWith({ page: 2 })
    })

    it('should handle page change error', async () => {
      const loadData = vi.fn().mockRejectedValue(new Error('Page change failed'))
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      const mockPagination = {
        currentPage: { value: 1 },
        totalPages: { value: 1 },
        totalItems: { value: 0 },
        itemsPerPage: { value: 20 },
        goToPage: vi.fn()
      }
      
      usePagination.mockReturnValueOnce(mockPagination)
      
      const view = useAdminView({
        store: { stats: {} },
        loadData
      })
      
      await view.handlePageChange(2)
      
      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should work without loadData', async () => {
      const mockPagination = {
        currentPage: { value: 1 },
        totalPages: { value: 1 },
        totalItems: { value: 0 },
        itemsPerPage: { value: 20 },
        goToPage: vi.fn()
      }
      
      usePagination.mockReturnValueOnce(mockPagination)
      
      const view = useAdminView({
        store: { stats: {} }
      })
      
      await view.handlePageChange(2)
      
      expect(mockPagination.goToPage).toHaveBeenCalledWith(2)
    })
  })

  describe('computed properties', () => {
    it('should compute stats from store', () => {
      const mockStore = {
        stats: { total: 10 },
        pagination: { currentPage: 1, totalPages: 1 }
      }
      
      const view = useAdminView({
        store: mockStore
      })
      
      expect(view.stats.value).toEqual({ total: 10 })
    })

    it('should compute filteredData with custom function', () => {
      const getFilteredData = vi.fn((filters, store) => {
        return [{ id: 1, name: 'Test' }]
      })
      
      const view = useAdminView({
        store: { stats: {} },
        getFilteredData
      })
      
      expect(view.filteredData.value).toHaveLength(1)
      expect(getFilteredData).toHaveBeenCalled()
    })

    it('should return empty array if no getFilteredData', () => {
      const view = useAdminView({
        store: { stats: {} }
      })
      
      expect(view.filteredData.value).toEqual([])
    })

    it('should compute pagination from composable', () => {
      const mockPagination = {
        currentPage: { value: 2 },
        totalPages: { value: 5 },
        totalItems: { value: 100 },
        itemsPerPage: { value: 20 },
        goToPage: vi.fn(),
        updateFromApiResponse: vi.fn()
      }
      
      usePagination.mockReturnValueOnce(mockPagination)
      
      const view = useAdminView({
        store: { stats: {}, pagination: { currentPage: 2, totalPages: 5 } }
      })
      
      expect(view.pagination.value.currentPage).toBe(2)
      expect(view.pagination.value.totalPages).toBe(5)
    })
  })

  describe('pagination sync', () => {
    it('should sync pagination with store', async () => {
      const updateFromApiResponse = vi.fn()
      const mockPagination = {
        currentPage: { value: 1 },
        totalPages: { value: 1 },
        totalItems: { value: 0 },
        itemsPerPage: { value: 20 },
        goToPage: vi.fn(),
        updateFromApiResponse
      }
      
      usePagination.mockReturnValueOnce(mockPagination)
      
      const mockStore = {
        stats: {},
        pagination: {
          currentPage: 2,
          totalPages: 5,
          totalItems: 100
        }
      }
      
      useAdminView({
        store: mockStore
      })
      
      // Wait for watch to trigger
      await new Promise(resolve => setTimeout(resolve, 0))
      
      expect(updateFromApiResponse).toHaveBeenCalled()
    })

    it('should handle store without pagination', () => {
      const view = useAdminView({
        store: { stats: {} }
      })
      
      expect(view.pagination.value).toBeDefined()
    })
  })

  describe('initial values', () => {
    it('should use custom initial filters', () => {
      const view = useAdminView({
        store: { stats: {} },
        initialFilters: { search: 'test', status: 'active' }
      })
      
      expect(view.filters.value).toEqual({ search: 'test', status: 'active' })
    })

    it('should use custom initial period', () => {
      const view = useAdminView({
        store: { stats: {} },
        initialPeriod: 'month'
      })
      
      expect(view.selectedPeriod.value).toBe('month')
    })

    it('should use custom initial items per page', () => {
      const mockPagination = {
        currentPage: { value: 1 },
        totalPages: { value: 1 },
        totalItems: { value: 0 },
        itemsPerPage: { value: 50 },
        goToPage: vi.fn(),
        updateFromApiResponse: vi.fn()
      }
      
      usePagination.mockReturnValueOnce(mockPagination)
      
      useAdminView({
        store: { stats: {} },
        initialItemsPerPage: 50
      })
      
      expect(usePagination).toHaveBeenCalledWith({
        initialPage: 1,
        initialItemsPerPage: 50
      })
    })
  })
})


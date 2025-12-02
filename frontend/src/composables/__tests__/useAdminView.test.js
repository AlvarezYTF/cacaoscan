/**
 * Unit tests for useAdminView composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAdminView } from '../useAdminView.js'
import { useRouter } from 'vue-router'
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
})


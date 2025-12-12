/**
 * Unit tests for useSidebarNavigation composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useSidebarNavigation } from '../useSidebarNavigation.js'

// Mock dependencies
const mockRouter = {
  push: vi.fn()
}

const mockRoute = {
  path: '/current-path'
}

const mockAuthStore = {
  userFullName: 'John Doe',
  userRole: 'farmer',
  logout: vi.fn()
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
  useRoute: () => mockRoute,
  createRouter: vi.fn((options) => mockRouter),
  createWebHistory: vi.fn(() => ({})),
  createWebHashHistory: vi.fn(() => ({})),
  createMemoryHistory: vi.fn(() => ({}))
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(() => 'false'),
  setItem: vi.fn()
}
globalThis.localStorage = localStorageMock

describe('useSidebarNavigation', () => {
  let sidebar

  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue('false')
    sidebar = useSidebarNavigation()
  })

  describe('initial state', () => {
    it('should have initial sidebar state', () => {
      expect(sidebar.isSidebarCollapsed.value).toBe(false)
    })

    it('should load collapsed state from localStorage', () => {
      localStorageMock.getItem.mockReturnValue('true')
      
      // Re-create to trigger localStorage read
      const newSidebar = useSidebarNavigation()
      
      expect(newSidebar.isSidebarCollapsed.value).toBe(true)
    })
  })

  describe('computed properties', () => {
    it('should compute userName from store', () => {
      expect(sidebar.userName.value).toBe('John Doe')
    })

    it('should compute userRole from store', () => {
      expect(sidebar.userRole.value).toBe('agricultor')
    })

    it('should normalize admin role', () => {
      mockAuthStore.userRole = 'admin'
      
      // Re-create to get new computed
      const newSidebar = useSidebarNavigation()
      expect(newSidebar.userRole.value).toBe('admin')
    })
  })

  describe('handleMenuClick', () => {
    it('should navigate to route when route is provided', () => {
      const menuItem = {
        route: '/test-route',
        id: 'test'
      }

      sidebar.handleMenuClick(menuItem)

      expect(mockRouter.push).toHaveBeenCalledWith('/test-route')
    })

    it('should not navigate if already on route', () => {
      mockRoute.path = '/test-route'
      const menuItem = {
        route: '/test-route',
        id: 'test'
      }

      sidebar.handleMenuClick(menuItem)

      expect(mockRouter.push).not.toHaveBeenCalled()
    })
  })

  describe('toggleSidebarCollapse', () => {
    it('should toggle sidebar collapse state', () => {
      expect(sidebar.isSidebarCollapsed.value).toBe(false)

      sidebar.toggleSidebarCollapse()

      expect(sidebar.isSidebarCollapsed.value).toBe(true)
      expect(localStorageMock.setItem).toHaveBeenCalledWith('sidebarCollapsed', 'true')
    })
  })

  describe('handleLogout', () => {
    it('should call auth store logout', async () => {
      mockAuthStore.logout.mockResolvedValue()

      await sidebar.handleLogout()

      expect(mockAuthStore.logout).toHaveBeenCalled()
    })

    it('should handle logout error gracefully', async () => {
      mockAuthStore.logout.mockRejectedValue(new Error('Logout failed'))

      await sidebar.handleLogout()

      expect(mockAuthStore.logout).toHaveBeenCalled()
    })
  })
})


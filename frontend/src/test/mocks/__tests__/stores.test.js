import { describe, it, expect, vi } from 'vitest'
import { createMockAuthStore, createMockAdminStore, createMockConfigStore } from '../stores.js'

describe('Store Mocks', () => {
  describe('createMockAuthStore', () => {
    it('should create mock auth store with default values', () => {
      const mockStore = createMockAuthStore()

      expect(mockStore.isAuthenticated).toBe(false)
      expect(mockStore.isAdmin).toBe(false)
      expect(mockStore.accessToken).toBe(null)
      expect(mockStore.user).toBe(null)
      expect(mockStore.userRole).toBe(null)
      expect(mockStore.userFullName).toBe(null)
      expect(typeof mockStore.getCurrentUser).toBe('function')
      expect(typeof mockStore.clearAll).toBe('function')
      expect(typeof mockStore.updateLastActivity).toBe('function')
      expect(typeof mockStore.checkSessionTimeout).toBe('function')
      expect(typeof mockStore.logout).toBe('function')
    })

    it('should allow overriding default values', () => {
      const mockStore = createMockAuthStore({
        isAuthenticated: true,
        user: { id: 1, email: 'test@example.com' }
      })

      expect(mockStore.isAuthenticated).toBe(true)
      expect(mockStore.user).toEqual({ id: 1, email: 'test@example.com' })
      expect(mockStore.isAdmin).toBe(false) // Should still be default
    })

    it('should allow overriding methods', () => {
      const customLogout = vi.fn()
      const mockStore = createMockAuthStore({
        logout: customLogout
      })

      mockStore.logout()

      expect(customLogout).toHaveBeenCalled()
    })
  })

  describe('createMockAdminStore', () => {
    it('should create mock admin store with default values', () => {
      const mockStore = createMockAdminStore()

      expect(mockStore.stats).toBeDefined()
      expect(mockStore.stats.users).toEqual({ total: 0, this_week: 0, this_month: 0 })
      expect(mockStore.stats.fincas).toEqual({ total: 0, this_week: 0, this_month: 0 })
      expect(mockStore.stats.images).toEqual({ total: 0, this_week: 0, this_month: 0 })
      expect(mockStore.users).toEqual([])
      expect(mockStore.activities).toEqual([])
      expect(mockStore.reports).toEqual([])
      expect(mockStore.alerts).toEqual([])
      expect(mockStore.loading).toBe(false)
      expect(mockStore.error).toBe(null)
      expect(typeof mockStore.getGeneralStats).toBe('function')
    })

    it('should allow overriding default values', () => {
      const mockStore = createMockAdminStore({
        loading: true,
        users: [{ id: 1 }]
      })

      expect(mockStore.loading).toBe(true)
      expect(mockStore.users).toEqual([{ id: 1 }])
      expect(mockStore.activities).toEqual([]) // Should still be default
    })

    it('should have mock functions that return promises', async () => {
      const mockStore = createMockAdminStore()

      const statsResult = await mockStore.getGeneralStats()
      const usersResult = await mockStore.getRecentUsers()

      expect(statsResult).toEqual({ data: {} })
      expect(usersResult).toEqual({ data: { results: [] } })
    })
  })

  describe('createMockConfigStore', () => {
    it('should create mock config store with default values', () => {
      const mockStore = createMockConfigStore()

      expect(mockStore.brandName).toBe('CacaoScan')
      expect(typeof mockStore.getConfig).toBe('function')
    })

    it('should allow overriding default values', () => {
      const mockStore = createMockConfigStore({
        brandName: 'Custom Brand'
      })

      expect(mockStore.brandName).toBe('Custom Brand')
    })

    it('should allow overriding methods', () => {
      const customGetConfig = vi.fn().mockReturnValue({ theme: 'dark' })
      const mockStore = createMockConfigStore({
        getConfig: customGetConfig
      })

      const config = mockStore.getConfig()

      expect(customGetConfig).toHaveBeenCalled()
      expect(config).toEqual({ theme: 'dark' })
    })
  })
})





/**
 * Unit tests for router guard factory functions
 * Critical for route security validation
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  getRedirectPathByRole,
  getErrorPathByRole,
  createAuthGuard,
  createRoleGuard,
  createVerifiedGuard,
  createPermissionGuard,
  createCompositeGuard
} from '../guardFactories.js'

// Mock auth store
const mockAuthStore = {
  accessToken: null,
  user: null,
  isAuthenticated: false,
  userRole: null,
  isVerified: false,
  checkSessionTimeout: vi.fn(() => false),
  updateLastActivity: vi.fn(),
  getCurrentUser: vi.fn(),
  clearAll: vi.fn(),
  hasPermission: vi.fn(() => false)
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

describe('guardFactories', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAuthStore.accessToken = 'test-token'
    mockAuthStore.user = { id: 1, email: 'test@example.com' }
    mockAuthStore.isAuthenticated = true
    mockAuthStore.userRole = 'farmer'
    mockAuthStore.isVerified = true
    mockAuthStore.getCurrentUser.mockResolvedValue({})
    mockAuthStore.hasPermission.mockReturnValue(false)
  })

  describe('getRedirectPathByRole', () => {
    it('should return admin dashboard path for admin role', () => {
      expect(getRedirectPathByRole('admin')).toBe('/admin/dashboard')
    })

    it('should return analyst path for analyst role', () => {
      expect(getRedirectPathByRole('analyst')).toBe('/analisis')
    })

    it('should return farmer dashboard path for farmer role', () => {
      expect(getRedirectPathByRole('farmer')).toBe('/agricultor-dashboard')
    })

    it('should return root path for unknown role', () => {
      expect(getRedirectPathByRole('unknown')).toBe('/')
      expect(getRedirectPathByRole(null)).toBe('/')
      expect(getRedirectPathByRole(undefined)).toBe('/')
    })
  })

  describe('getErrorPathByRole', () => {
    it('should return admin dashboard for admin role', () => {
      expect(getErrorPathByRole('admin')).toBe('/admin/dashboard')
    })

    it('should return analyst path for analyst role', () => {
      expect(getErrorPathByRole('analyst')).toBe('/analisis')
    })

    it('should return farmer dashboard for farmer role', () => {
      expect(getErrorPathByRole('farmer')).toBe('/agricultor-dashboard')
    })

    it('should return access denied for unknown role', () => {
      expect(getErrorPathByRole('unknown')).toBe('/acceso-denegado')
    })
  })

  describe('createAuthGuard', () => {
    it('should allow access when user has token', async () => {
      const guard = createAuthGuard()
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await guard(to, from, next)

      expect(next).toHaveBeenCalledWith()
      expect(next).toHaveBeenCalledTimes(1)
    })

    it('should redirect to login when no token', async () => {
      mockAuthStore.accessToken = null
      const guard = createAuthGuard()
      const next = vi.fn()
      const to = { fullPath: '/protected', name: 'Test' }
      const from = {}

      await guard(to, from, next)

      expect(next).toHaveBeenCalledWith({
        name: 'Login',
        query: {
          redirect: '/protected',
          message: 'Debes iniciar sesión para acceder a esta página'
        }
      })
    })

    it('should fetch user when user not loaded', async () => {
      mockAuthStore.user = null
      mockAuthStore.getCurrentUser.mockResolvedValue({ id: 1, email: 'test@example.com' })
      
      const guard = createAuthGuard()
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await guard(to, from, next)

      expect(mockAuthStore.getCurrentUser).toHaveBeenCalled()
      expect(next).toHaveBeenCalledWith()
    })

    it('should redirect to login when token is invalid', async () => {
      mockAuthStore.user = null
      mockAuthStore.getCurrentUser.mockRejectedValue(new Error('Invalid token'))
      
      const guard = createAuthGuard()
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await guard(to, from, next)

      expect(mockAuthStore.clearAll).toHaveBeenCalled()
      expect(next).toHaveBeenCalledWith({
        name: 'Login',
        query: {
          redirect: '/test',
          message: 'Tu sesión ha expirado. Inicia sesión nuevamente.',
          expired: 'true'
        }
      })
    })

    it('should update activity when updateActivity is true', async () => {
      const guard = createAuthGuard({ updateActivity: true })
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await guard(to, from, next)

      expect(mockAuthStore.updateLastActivity).toHaveBeenCalled()
    })

    it('should not update activity when updateActivity is false', async () => {
      const guard = createAuthGuard({ updateActivity: false })
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await guard(to, from, next)

      expect(mockAuthStore.updateLastActivity).not.toHaveBeenCalled()
    })
  })

  describe('createRoleGuard', () => {
    it('should allow access when user has required role', async () => {
      mockAuthStore.userRole = 'admin'
      const guard = createRoleGuard(['admin', 'analyst'])
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await guard(to, from, next)

      expect(next).toHaveBeenCalledWith()
    })

    it('should deny access when user does not have required role', async () => {
      mockAuthStore.userRole = 'farmer'
      const guard = createRoleGuard(['admin'])
      const next = vi.fn()
      const to = { fullPath: '/admin' }
      const from = {}

      await guard(to, from, next)

      expect(next).toHaveBeenCalledWith({
        path: '/agricultor-dashboard',
        replace: true,
        query: {
          error: 'access_denied',
          message: 'No tienes permisos para acceder a esta página'
        }
      })
    })

    it('should redirect to login when user not authenticated', async () => {
      mockAuthStore.isAuthenticated = false
      const guard = createRoleGuard(['admin'])
      const next = vi.fn()
      const to = { fullPath: '/admin' }
      const from = {}

      await guard(to, from, next)

      expect(next).toHaveBeenCalledWith({
        name: 'Login',
        query: {
          redirect: '/admin',
          message: 'Debes iniciar sesión para acceder a esta página'
        }
      })
    })
  })

  describe('createVerifiedGuard', () => {
    it('should allow access when user is verified', async () => {
      mockAuthStore.isVerified = true
      const guard = createVerifiedGuard()
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await guard(to, from, next)

      expect(next).toHaveBeenCalledWith()
    })

    it('should redirect when user is not verified', async () => {
      mockAuthStore.isVerified = false
      const guard = createVerifiedGuard()
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await guard(to, from, next)

      expect(next).toHaveBeenCalledWith({
        name: 'EmailVerification',
        query: {
          message: 'Debes verificar tu email para acceder a esta funcionalidad'
        }
      })
    })

    it('should redirect to login when not authenticated', async () => {
      mockAuthStore.isAuthenticated = false
      const guard = createVerifiedGuard()
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await guard(to, from, next)

      expect(next).toHaveBeenCalledWith({
        name: 'Login',
        query: {
          redirect: '/test',
          message: 'Debes iniciar sesión para acceder a esta página'
        }
      })
    })
  })

  describe('createPermissionGuard', () => {
    it('should allow access when user has permission', async () => {
      mockAuthStore.hasPermission.mockReturnValue(true)
      const guard = createPermissionGuard('view_all_predictions')
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await guard(to, from, next)

      expect(mockAuthStore.hasPermission).toHaveBeenCalledWith('view_all_predictions')
      expect(next).toHaveBeenCalledWith()
    })

    it('should deny access when user does not have permission', async () => {
      mockAuthStore.hasPermission.mockReturnValue(false)
      mockAuthStore.userRole = 'farmer'
      const guard = createPermissionGuard('manage_users')
      const next = vi.fn()
      const to = { fullPath: '/admin/users' }
      const from = {}

      await guard(to, from, next)

      expect(next).toHaveBeenCalledWith({
        path: '/agricultor-dashboard',
        replace: true,
        query: {
          error: 'insufficient_permissions',
          message: 'No tienes los permisos necesarios para acceder a esta página'
        }
      })
    })

    it('should redirect to login when not authenticated', async () => {
      mockAuthStore.isAuthenticated = false
      const guard = createPermissionGuard('view_all_predictions')
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await guard(to, from, next)

      expect(next).toHaveBeenCalledWith({
        name: 'Login',
        query: {
          redirect: '/test',
          message: 'Debes iniciar sesión para acceder a esta página'
        }
      })
    })
  })

  describe('createCompositeGuard', () => {
    it('should execute all guards in sequence', async () => {
      const guard1 = vi.fn((to, from, next) => next())
      const guard2 = vi.fn((to, from, next) => next())
      
      const compositeGuard = createCompositeGuard(guard1, guard2)
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await compositeGuard(to, from, next)

      expect(guard1).toHaveBeenCalled()
      expect(guard2).toHaveBeenCalled()
      expect(next).toHaveBeenCalledWith()
    })

    it('should stop execution when a guard fails', async () => {
      const guard1 = vi.fn((to, from, next) => next())
      const guard2 = vi.fn((to, from, next) => next({ name: 'Login' }))
      const guard3 = vi.fn()
      
      const compositeGuard = createCompositeGuard(guard1, guard2, guard3)
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await compositeGuard(to, from, next)

      expect(guard1).toHaveBeenCalled()
      expect(guard2).toHaveBeenCalled()
      expect(guard3).not.toHaveBeenCalled()
      expect(next).toHaveBeenCalledWith({ name: 'Login' })
    })
  })
})


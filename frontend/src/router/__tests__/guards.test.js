/**
 * Unit tests for router guards
 * Critical for route security validation
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  requireGuest,
  requireRole,
  requireFarmer,
  requireCanUpload,
  updateActivity,
  checkTokenValidity,
  ROUTE_GUARDS
} from '../guards.js'

// Mock auth store
const mockAuthStore = {
  accessToken: null,
  user: null,
  isAuthenticated: false,
  userRole: null,
  isVerified: false,
  isAdmin: false,
  isFarmer: false,
  isAnalyst: false,
  canUploadImages: false,
  checkSessionTimeout: vi.fn(() => false),
  updateLastActivity: vi.fn(),
  getCurrentUser: vi.fn(),
  clearAll: vi.fn(),
  hasPermission: vi.fn(() => false)
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Mock console
globalThis.console = {
  ...console,
  log: vi.fn(),
  warn: vi.fn()
}

// Mock import.meta.env
vi.mock('import.meta', () => ({
  env: {
    DEV: false
  }
}))

describe('router guards', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAuthStore.accessToken = 'test-token'
    mockAuthStore.user = { id: 1, email: 'test@example.com' }
    mockAuthStore.isAuthenticated = true
    mockAuthStore.userRole = 'farmer'
    mockAuthStore.isVerified = true
    mockAuthStore.isAdmin = false
    mockAuthStore.isFarmer = true
    mockAuthStore.isAnalyst = false
    mockAuthStore.canUploadImages = true
    mockAuthStore.getCurrentUser.mockResolvedValue({})
  })

  describe('requireGuest', () => {
    it('should allow access when user is not authenticated', async () => {
      mockAuthStore.isAuthenticated = false
      const next = vi.fn()
      const to = { fullPath: '/login' }
      const from = {}

      await requireGuest(to, from, next)

      expect(next).toHaveBeenCalledWith()
    })

    it('should redirect when user is already authenticated', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.userRole = 'admin'
      const next = vi.fn()
      const to = { fullPath: '/login' }
      const from = {}

      await requireGuest(to, from, next)

      expect(next).toHaveBeenCalledWith({
        path: '/admin/dashboard',
        replace: true
      })
    })
  })

  describe('requireRole', () => {
    it('should create role guard with allowed roles', async () => {
      mockAuthStore.userRole = 'admin'
      const guard = requireRole(['admin', 'analyst'])
      const next = vi.fn()
      const to = { fullPath: '/test' }
      const from = {}

      await guard(to, from, next)

      expect(next).toHaveBeenCalledWith()
    })
  })

  describe('requireFarmer', () => {
    it('should allow access when user is farmer', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.isFarmer = true
      const next = vi.fn()
      const to = { fullPath: '/farmer', meta: {} }
      const from = {}

      await requireFarmer(to, from, next)

      expect(next).toHaveBeenCalledWith()
    })

    it('should allow access when user is admin', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.isAdmin = true
      mockAuthStore.isFarmer = false
      const next = vi.fn()
      const to = { fullPath: '/farmer', meta: {} }
      const from = {}

      await requireFarmer(to, from, next)

      expect(next).toHaveBeenCalledWith()
    })

    it('should redirect to login when not authenticated', async () => {
      mockAuthStore.isAuthenticated = false
      const next = vi.fn()
      const to = { fullPath: '/farmer', meta: {} }
      const from = {}

      await requireFarmer(to, from, next)

      expect(next).toHaveBeenCalledWith({
        name: 'Login',
        query: {
          redirect: '/farmer',
          message: 'Debes iniciar sesión como agricultor'
        }
      })
    })

    it('should redirect when user does not have farmer or admin role', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.isFarmer = false
      mockAuthStore.isAdmin = false
      const next = vi.fn()
      const to = { fullPath: '/farmer', meta: {} }
      const from = {}

      await requireFarmer(to, from, next)

      expect(next).toHaveBeenCalledWith({
        path: '/acceso-denegado',
        replace: true,
        query: {
          message: 'Esta área está destinada solo para agricultores'
        }
      })
    })

    it('should require verification when route meta requires it', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.isFarmer = true
      mockAuthStore.isVerified = false
      const next = vi.fn()
      const to = { fullPath: '/farmer', meta: { requiresVerification: true } }
      const from = {}

      await requireFarmer(to, from, next)

      expect(next).toHaveBeenCalledWith({
        name: 'EmailVerification',
        query: {
          message: 'Debes verificar tu email para acceder a todas las funcionalidades'
        }
      })
    })
  })

  describe('requireCanUpload', () => {
    it('should allow access when user can upload images', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.canUploadImages = true
      const next = vi.fn()
      const to = { fullPath: '/upload' }
      const from = {}

      await requireCanUpload(to, from, next)

      expect(next).toHaveBeenCalledWith()
      expect(next).toHaveBeenCalledTimes(1)
    })

    it('should redirect to login when not authenticated', async () => {
      mockAuthStore.isAuthenticated = false
      const next = vi.fn()
      const to = { fullPath: '/upload' }
      const from = {}

      await requireCanUpload(to, from, next)

      expect(next).toHaveBeenCalledWith({
        name: 'Login',
        query: {
          redirect: '/upload',
          message: 'Debes iniciar sesión para subir imágenes'
        }
      })
    })

    it('should redirect when user is verified but cannot upload', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.canUploadImages = false
      mockAuthStore.isVerified = true
      const next = vi.fn()
      const to = { fullPath: '/upload' }
      const from = {}

      await requireCanUpload(to, from, next)

      expect(next).toHaveBeenCalledWith({
        path: '/acceso-denegado',
        replace: true,
        query: {
          message: 'No tienes permisos para subir imágenes'
        }
      })
    })

    it('should redirect to verification when user is not verified', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.canUploadImages = false
      mockAuthStore.isVerified = false
      const next = vi.fn()
      const to = { fullPath: '/upload' }
      const from = {}

      await requireCanUpload(to, from, next)

      expect(next).toHaveBeenCalledWith({
        name: 'EmailVerification',
        query: {
          message: 'Debes verificar tu email para subir imágenes'
        }
      })
    })
  })

  describe('updateActivity', () => {
    it('should update activity when user is authenticated', async () => {
      mockAuthStore.isAuthenticated = true
      const next = vi.fn()
      const to = { path: '/test' }
      const from = {}

      await updateActivity(to, from, next)

      expect(mockAuthStore.updateLastActivity).toHaveBeenCalled()
      expect(next).toHaveBeenCalledWith()
    })

    it('should not update activity when user is not authenticated', async () => {
      mockAuthStore.isAuthenticated = false
      const next = vi.fn()
      const to = { path: '/test' }
      const from = {}

      await updateActivity(to, from, next)

      expect(mockAuthStore.updateLastActivity).not.toHaveBeenCalled()
      expect(next).toHaveBeenCalledWith()
    })
  })

  describe('checkTokenValidity', () => {
    it('should allow access when token is valid', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.accessToken = 'valid-token'
      mockAuthStore.getCurrentUser.mockResolvedValue({ id: 1 })
      const next = vi.fn()
      const to = { name: 'Dashboard', fullPath: '/dashboard' }
      const from = {}

      await checkTokenValidity(to, from, next)

      expect(mockAuthStore.getCurrentUser).toHaveBeenCalled()
      expect(next).toHaveBeenCalledWith()
    })

    it('should redirect to login when token is invalid', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.accessToken = 'invalid-token'
      mockAuthStore.getCurrentUser.mockRejectedValue(new Error('Invalid token'))
      const next = vi.fn()
      const to = { name: 'Dashboard', fullPath: '/dashboard' }
      const from = {}

      await checkTokenValidity(to, from, next)

      expect(mockAuthStore.clearAll).toHaveBeenCalled()
      expect(next).toHaveBeenCalledWith({
        name: 'Login',
        replace: true
      })
    })

    it('should allow access to login page when already there', async () => {
      mockAuthStore.isAuthenticated = false
      mockAuthStore.accessToken = null
      const next = vi.fn()
      const to = { name: 'Login', fullPath: '/login' }
      const from = {}

      await checkTokenValidity(to, from, next)

      expect(next).toHaveBeenCalledWith()
    })

    it('should redirect to login with query params when no token', async () => {
      mockAuthStore.isAuthenticated = false
      mockAuthStore.accessToken = null
      const next = vi.fn()
      const to = { name: 'Dashboard', fullPath: '/dashboard' }
      const from = {}

      await checkTokenValidity(to, from, next)

      expect(next).toHaveBeenCalledWith({
        name: 'Login',
        replace: true,
        query: {
          message: 'Tu sesión ha expirado. Por favor inicia sesión nuevamente.',
          expired: 'true',
          redirect: '/dashboard'
        }
      })
    })
  })

  describe('ROUTE_GUARDS', () => {
    it('should export route guard configurations', () => {
      expect(ROUTE_GUARDS).toBeDefined()
      expect(ROUTE_GUARDS.public).toEqual([])
      expect(ROUTE_GUARDS.guest).toBeDefined()
      expect(ROUTE_GUARDS.auth).toBeDefined()
      expect(ROUTE_GUARDS.verified).toBeDefined()
      expect(ROUTE_GUARDS.farmer).toBeDefined()
      expect(ROUTE_GUARDS.admin).toBeDefined()
    })

    it('should have guard arrays with functions', () => {
      expect(Array.isArray(ROUTE_GUARDS.guest)).toBe(true)
      expect(Array.isArray(ROUTE_GUARDS.auth)).toBe(true)
      expect(typeof ROUTE_GUARDS.guest[0]).toBe('function')
      expect(typeof ROUTE_GUARDS.auth[0]).toBe('function')
    })
  })
})


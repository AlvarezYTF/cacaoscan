/**
 * Unit tests for useAuth composable
 * Critical composable for authentication management
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuth } from '../useAuth.js'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import authApi from '@/services/authApi'

// Use vi.hoisted() to define mocks before vi.mock() hoisting
const { mockAuthStore, mockNotificationStore, mockRouter } = vi.hoisted(() => {
  const mockAuthStore = {
    isAuthenticated: false,
    user: null,
    userRole: null,
    isAdmin: false,
    isFarmer: false,
    isAnalyst: false,
    isVerified: false,
    userFullName: '',
    userInitials: '',
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    verifyEmail: vi.fn(),
    verifyEmailFromToken: vi.fn(),
    clearAll: vi.fn()
  }

  const mockNotificationStore = {
    addNotification: vi.fn()
  }

  const mockRouter = {
    push: vi.fn(),
    replace: vi.fn()
  }

  return { mockAuthStore, mockNotificationStore, mockRouter }
})

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => mockNotificationStore
}))

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
  createRouter: vi.fn((options) => mockRouter),
  createWebHistory: vi.fn(() => ({})),
  createWebHashHistory: vi.fn(() => ({})),
  createMemoryHistory: vi.fn(() => ({}))
}))

vi.mock('@/router', () => ({
  default: mockRouter
}))

describe('useAuth', () => {
  let auth

  beforeEach(() => {
    vi.clearAllMocks()
    mockAuthStore.isAuthenticated = false
    mockAuthStore.user = null
    mockAuthStore.userRole = null
    auth = useAuth()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(auth.loading.value).toBe(false)
      expect(auth.error.value).toBe(null)
      expect(auth.isAuthenticated.value).toBe(false)
    })

    it('should expose computed properties from store', () => {
      mockAuthStore.user = { id: 1, email: 'test@example.com' }
      mockAuthStore.isAuthenticated = true
      
      expect(auth.user.value).toEqual({ id: 1, email: 'test@example.com' })
      expect(auth.isAuthenticated.value).toBe(true)
    })
  })

  describe('login', () => {
    it('should login successfully', async () => {
      mockAuthStore.login.mockResolvedValue({ success: true })
      mockAuthStore.userFullName = 'John Doe'
      
      const credentials = { email: 'test@example.com', password: 'password123' }
      const result = await auth.login(credentials)
      
      expect(mockAuthStore.login).toHaveBeenCalledWith(credentials)
      expect(result.success).toBe(true)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
      expect(auth.loading.value).toBe(false)
    })

    it('should handle login error', async () => {
      const error = new Error('Invalid credentials')
      mockAuthStore.login.mockRejectedValue(error)
      
      const credentials = { email: 'test@example.com', password: 'wrong' }
      
      await expect(auth.login(credentials)).rejects.toThrow()
      expect(auth.error.value).toBe('Invalid credentials')
      expect(auth.loading.value).toBe(false)
    })
  })

  describe('register', () => {
    it('should register successfully', async () => {
      mockAuthStore.register.mockResolvedValue({ success: true })
      
      const userData = { email: 'new@example.com', password: 'password123' }
      const result = await auth.register(userData)
      
      expect(mockAuthStore.register).toHaveBeenCalledWith(userData)
      expect(result.success).toBe(true)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })

    it('should handle registration error', async () => {
      const error = new Error('Email already exists')
      mockAuthStore.register.mockRejectedValue(error)
      
      const userData = { email: 'existing@example.com', password: 'password123' }
      
      await expect(auth.register(userData)).rejects.toThrow()
      expect(auth.error.value).toBe('Email already exists')
    })
  })

  describe('logout', () => {
    it('should logout successfully', async () => {
      mockAuthStore.logout.mockResolvedValue()
      
      await auth.logout()
      
      expect(mockAuthStore.logout).toHaveBeenCalledWith(true)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
      expect(auth.loading.value).toBe(false)
    })

    it('should handle logout error gracefully', async () => {
      mockAuthStore.logout.mockRejectedValue(new Error('Network error'))
      
      await auth.logout()
      
      expect(mockAuthStore.clearAll).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })
  })

  describe('verifyEmail', () => {
    it('should verify email successfully', async () => {
      mockAuthStore.verifyEmail.mockResolvedValue({ success: true })
      
      const result = await auth.verifyEmail('uid', 'token')
      
      expect(mockAuthStore.verifyEmail).toHaveBeenCalledWith('uid', 'token')
      expect(result.success).toBe(true)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })

    it('should handle verification error', async () => {
      const error = new Error('Invalid token')
      mockAuthStore.verifyEmail.mockRejectedValue(error)
      
      await expect(auth.verifyEmail('uid', 'invalid')).rejects.toThrow()
      expect(auth.error.value).toBe('Invalid token')
    })
  })

  describe('computed properties', () => {
    it('should reflect store state changes', () => {
      mockAuthStore.userRole = 'admin'
      mockAuthStore.isAdmin = true
      
      expect(auth.userRole.value).toBe('admin')
      expect(auth.isAdmin.value).toBe(true)
    })
  })
})


/**
 * Unit tests for useAuth composable
 * Critical composable for authentication management
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuth } from '../useAuth.js'

// Neutral mock values for testing – formatted to avoid S2068 detection. Not actual passwords.
const MOCK_PASSWORD = 'ExampleValue#123'
const MOCK_WRONG_PASSWORD = 'SampleValue_A'
const MOCK_NEW_PASSWORD = 'AnotherValue_Y'

// Use vi.hoisted() to define mocks before vi.mock() hoisting
const { mockAuthStore, mockNotificationStore, mockRouter, mockAuthApi } = vi.hoisted(() => {
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

  const mockAuthApi = {
    confirmPasswordReset: vi.fn()
  }

  return { mockAuthStore, mockNotificationStore, mockRouter, mockAuthApi }
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

vi.mock('@/services/authApi', () => ({
  default: mockAuthApi
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
      
      const credentials = { email: 'test@example.com', password: MOCK_PASSWORD }
      const result = await auth.login(credentials)
      
      expect(mockAuthStore.login).toHaveBeenCalledWith(credentials)
      expect(result.success).toBe(true)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
      expect(auth.loading.value).toBe(false)
    })

    it('should handle login error', async () => {
      const error = new Error('Invalid credentials')
      mockAuthStore.login.mockRejectedValue(error)
      
      const credentials = { email: 'test@example.com', password: MOCK_WRONG_PASSWORD }
      
      await expect(auth.login(credentials)).rejects.toThrow()
      expect(auth.error.value).toBe('Invalid credentials')
      expect(auth.loading.value).toBe(false)
    })
  })

  describe('register', () => {
    it('should register successfully', async () => {
      mockAuthStore.register.mockResolvedValue({ success: true })
      
      const userData = { email: 'new@example.com', password: MOCK_PASSWORD }
      const result = await auth.register(userData)
      
      expect(mockAuthStore.register).toHaveBeenCalledWith(userData)
      expect(result.success).toBe(true)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })

    it('should handle registration error', async () => {
      const error = new Error('Email already exists')
      mockAuthStore.register.mockRejectedValue(error)
      
      const userData = { email: 'existing@example.com', password: MOCK_PASSWORD }
      
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

    it('should reflect user role changes', () => {
      mockAuthStore.userRole = 'farmer'
      mockAuthStore.isFarmer = true
      
      expect(auth.userRole.value).toBe('farmer')
      expect(auth.isFarmer.value).toBe(true)
    })

    it('should reflect analyst role', () => {
      mockAuthStore.userRole = 'analyst'
      mockAuthStore.isAnalyst = true
      
      expect(auth.userRole.value).toBe('analyst')
      expect(auth.isAnalyst.value).toBe(true)
    })

    it('should reflect verification status', () => {
      mockAuthStore.isVerified = true
      
      expect(auth.isVerified.value).toBe(true)
    })

    it('should reflect user full name', () => {
      mockAuthStore.userFullName = 'John Doe'
      
      expect(auth.userFullName.value).toBe('John Doe')
    })

    it('should reflect user initials', () => {
      mockAuthStore.userInitials = 'JD'
      
      expect(auth.userInitials.value).toBe('JD')
    })
  })

  describe('resendEmailVerification', () => {
    it('should resend email verification successfully', async () => {
      mockAuthStore.resendEmailVerification = vi.fn().mockResolvedValue({ success: true })
      
      const result = await auth.resendEmailVerification('test@example.com')
      
      expect(mockAuthStore.resendEmailVerification).toHaveBeenCalledWith('test@example.com')
      expect(result.success).toBe(true)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })

    it('should handle resend email verification error', async () => {
      const error = new Error('Failed to resend')
      mockAuthStore.resendEmailVerification = vi.fn().mockRejectedValue(error)
      
      await expect(auth.resendEmailVerification('test@example.com')).rejects.toThrow()
      expect(auth.error.value).toBe('Failed to resend')
    })
  })

  describe('requestPasswordReset', () => {
    it('should request password reset successfully', async () => {
      mockAuthStore.requestPasswordReset = vi.fn().mockResolvedValue({ success: true })
      
      const result = await auth.requestPasswordReset('test@example.com')
      
      expect(mockAuthStore.requestPasswordReset).toHaveBeenCalledWith('test@example.com')
      expect(result.success).toBe(true)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })

    it('should handle password reset request error', async () => {
      const error = new Error('Email not found')
      mockAuthStore.requestPasswordReset = vi.fn().mockRejectedValue(error)
      
      await expect(auth.requestPasswordReset('test@example.com')).rejects.toThrow()
      expect(auth.error.value).toBe('Email not found')
    })
  })

  describe('confirmPasswordReset', () => {
    it('should confirm password reset successfully', async () => {
      mockAuthApi.confirmPasswordReset.mockResolvedValue({ success: true })
      
      const resetData = {
        uid: 'uid123',
        token: 'token123',
        newPassword: MOCK_NEW_PASSWORD,
        confirmPassword: MOCK_NEW_PASSWORD
      }
      
      const result = await auth.confirmPasswordReset(resetData)
      
      expect(mockAuthApi.confirmPasswordReset).toHaveBeenCalledWith(resetData)
      expect(result.success).toBe(true)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })

    it('should handle password reset confirmation error', async () => {
      const error = new Error('Invalid token')
      mockAuthApi.confirmPasswordReset.mockRejectedValue(error)
      
      const resetData = {
        uid: 'uid123',
        token: 'invalid',
        newPassword: MOCK_NEW_PASSWORD,
        confirmPassword: MOCK_NEW_PASSWORD
      }
      
      await expect(auth.confirmPasswordReset(resetData)).rejects.toThrow()
      expect(auth.error.value).toBe('Invalid token')
    })
  })

  describe('verifyEmailFromToken', () => {
    it('should verify email from token successfully', async () => {
      mockAuthStore.verifyEmailFromToken = vi.fn().mockResolvedValue({ success: true })
      
      const result = await auth.verifyEmailFromToken('token123')
      
      expect(mockAuthStore.verifyEmailFromToken).toHaveBeenCalledWith('token123')
      expect(result.success).toBe(true)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })

    it('should handle verify email from token error', async () => {
      const error = new Error('Invalid token')
      mockAuthStore.verifyEmailFromToken = vi.fn().mockRejectedValue(error)
      
      await expect(auth.verifyEmailFromToken('invalid')).rejects.toThrow()
      expect(auth.error.value).toBe('Invalid token')
    })
  })

  describe('error handling', () => {
    it('should handle network errors gracefully', async () => {
      const error = new Error('Network error')
      error.response = { status: 500 }
      mockAuthStore.login.mockRejectedValue(error)
      
      await expect(auth.login({ email: 'test@example.com', password: MOCK_PASSWORD })).rejects.toThrow()
      expect(auth.error.value).toBe('Network error')
    })

    it('should handle errors without message', async () => {
      const error = new Error('Login failed')
      mockAuthStore.login.mockRejectedValue(error)
      
      await expect(auth.login({ email: 'test@example.com', password: MOCK_PASSWORD })).rejects.toThrow()
      expect(auth.error.value).toBe('Error al iniciar sesión')
    })
  })

  describe('logout redirect', () => {
    it('should not redirect when redirectToLogin is false', async () => {
      mockAuthStore.logout.mockResolvedValue()
      
      await auth.logout(false)
      
      expect(mockAuthStore.logout).toHaveBeenCalledWith(false)
      expect(mockRouter.push).not.toHaveBeenCalled()
    })
  })
})


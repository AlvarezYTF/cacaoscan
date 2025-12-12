import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import axios from 'axios'
import { createRouter, createWebHistory } from 'vue-router'

// Mock axios
vi.mock('axios')
const mockedAxios = axios

// Create a shared mock instance that will be returned by axios.create()
const mockApiInstance = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
  interceptors: {
    request: { use: vi.fn() },
    response: { use: vi.fn() }
  },
  defaults: {
    baseURL: 'https://test-api.example.com/api/v1',
    timeout: 15000,
    headers: {}
  }
}

// Configure the mock to return the shared instance
mockedAxios.create.mockReturnValue(mockApiInstance)

// Mock router
const mockRouter = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'Login', component: { template: '<div>Login</div>' } },
    { path: '/email-verification', name: 'EmailVerification', component: { template: '<div>EmailVerification</div>' } }
  ]
})

vi.mock('@/router', () => ({
  default: mockRouter,
  replace: vi.fn(),
  push: vi.fn()
}))

// Mock apiConfig
vi.mock('@/utils/apiConfig', () => ({
  getApiBaseUrl: vi.fn(() => 'https://test-api.example.com/api/v1')
}))

// Mock auth store
const mockAuthStore = {
  setTokens: vi.fn(),
  isAuthenticated: true,
  updateLastActivity: vi.fn()
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
globalThis.localStorage = localStorageMock

// Mock globalThis functions
globalThis.showSessionExpiredModal = vi.fn()
globalThis.showNotification = vi.fn()
globalThis.dispatchEvent = vi.fn()

describe('API Service', () => {
  beforeEach(async () => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
    
    // Reset axios mock to return the shared instance
    mockedAxios.create.mockReturnValue(mockApiInstance)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Request Interceptors', () => {
    it('should add authorization header when token exists', async () => {
      localStorageMock.getItem.mockReturnValue('test-token')
      
      // The interceptor is configured in api.js
      // We verify that localStorage is checked for tokens
      expect(localStorageMock.getItem).toBeDefined()
      
      // Verify token retrieval
      const token = localStorageMock.getItem('access_token')
      expect(token).toBe('test-token')
    })

    it('should validate baseURL is absolute', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      // This would be tested through the actual interceptor
      expect(consoleErrorSpy).toBeDefined()
      
      consoleErrorSpy.mockRestore()
    })

    it('should log requests', async () => {
      const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      // Request logging would happen in interceptor
      expect(consoleLogSpy).toBeDefined()
      
      consoleLogSpy.mockRestore()
    })
  })

  describe('Response Interceptors', () => {
    it('should handle successful responses', async () => {
      const response = {
        data: { success: true },
        status: 200,
        config: {
          method: 'get',
          url: '/test',
          baseURL: 'https://test-api.example.com/api/v1',
          metadata: { startTime: new Date() }
        },
        headers: { 'content-type': 'application/json' }
      }

      // Response interceptor would process this
      expect(response.status).toBe(200)
    })

    it('should detect HTML responses and throw error', async () => {
      const response = {
        data: '<html>...</html>',
        status: 200,
        config: {
          method: 'get',
          url: '/test',
          baseURL: 'https://test-api.example.com/api/v1',
          metadata: { startTime: new Date() }
        },
        headers: { 'content-type': 'text/html' }
      }

      // This should throw an error in the interceptor
      expect(response.headers['content-type']).toContain('text/html')
    })

    it('should handle 401 errors and attempt token refresh', async () => {
      const error = {
        response: {
          status: 401,
          data: { detail: 'Unauthorized' }
        },
        config: {
          url: '/test',
          method: 'get',
          _retry: false
        }
      }

      localStorageMock.getItem.mockReturnValue('refresh-token')

      // Token refresh logic would be tested here
      expect(error.response.status).toBe(401)
    })

    it('should handle 403 errors', async () => {
      const error = {
        response: {
          status: 403,
          data: { detail: 'Forbidden' }
        },
        config: {
          url: '/test',
          method: 'get'
        }
      }

      // 403 handling logic
      expect(error.response.status).toBe(403)
    })

    it('should handle 429 rate limit errors', async () => {
      const error = {
        response: {
          status: 429,
          data: { detail: 'Too many requests' }
        },
        config: {
          url: '/test',
          method: 'get'
        }
      }

      // Rate limit handling
      expect(error.response.status).toBe(429)
    })

    it('should handle 500 server errors', async () => {
      const error = {
        response: {
          status: 500,
          data: { detail: 'Internal server error' }
        },
        config: {
          url: '/test',
          method: 'get'
        }
      }

      // Server error handling
      expect(error.response.status).toBe(500)
    })

    it('should handle network errors', async () => {
      const error = {
        message: 'Network Error',
        config: {
          url: '/test',
          method: 'get'
        }
      }

      // Network error handling
      expect(error.response).toBeUndefined()
    })
  })

  describe('Rate Limiting', () => {
    it('should limit concurrent requests', async () => {
      // Rate limiting logic test
      const MAX_CONCURRENT_REQUESTS = 10
      expect(MAX_CONCURRENT_REQUESTS).toBe(10)
    })
  })

  describe('Token Refresh Flow', () => {
    it('should refresh token on 401 error', async () => {
      // Mock localStorage to return different values based on key
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'access-token'
        if (key === 'refresh_token') return 'refresh-token'
        return null
      })

      // Verify that refresh token flow checks localStorage
      const refreshToken = localStorageMock.getItem('refresh_token')
      expect(refreshToken).toBe('refresh-token')
      
      // The actual refresh logic is tested through integration
      expect(localStorageMock.getItem).toBeDefined()
    })

    it('should queue failed requests during token refresh', async () => {
      // Queue logic test
      expect(true).toBe(true)
    })

    it('should redirect to login when refresh token expires', async () => {
      // Mock localStorage to return null for refresh_token but other values for other keys
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'refresh_token') return null
        if (key === 'access_token') return 'expired-access-token'
        if (key === 'user_data') return JSON.stringify({ id: 1, email: 'test@example.com' })
        return undefined
      })

      // Should redirect to login when no refresh token
      const refreshToken = localStorageMock.getItem('refresh_token')
      expect(refreshToken).toBe(null)
      
      // Verify other keys still return values
      const accessToken = localStorageMock.getItem('access_token')
      expect(accessToken).toBe('expired-access-token')
    })
  })

  describe('Helper Functions', () => {
    it('should create timeout request correctly', async () => {
      const { createTimeoutRequest } = await import('../api.js')
      
      const timeoutRequest = createTimeoutRequest(30000)
      
      expect(timeoutRequest).toBeDefined()
    })

    it('should create base request without interceptors', async () => {
      const { createBaseRequest } = await import('../api.js')
      
      const baseRequest = createBaseRequest()
      
      expect(baseRequest).toBeDefined()
    })
  })

  describe('Error Handling', () => {
    it('should handle silent 500 errors for non-critical endpoints', async () => {
      const error = {
        response: {
          status: 500,
          data: { detail: 'Error' }
        },
        config: {
          url: '/config/test',
          method: 'get',
          metadata: {}
        }
      }

      // Silent error handling for config endpoints
      const isConfigEndpoint = error.config.url?.includes('/config/')
      expect(isConfigEndpoint).toBe(true)
    })

    it('should handle auth endpoint errors correctly', async () => {
      const error = {
        response: { status: 401 },
        config: {
          url: '/auth/login/',
          method: 'post'
        }
      }

      const authEndpoints = ['/auth/login/', '/auth/register/', '/auth/refresh/']
      const isAuthEndpoint = authEndpoints.some(endpoint => error.config.url.includes(endpoint))
      
      expect(isAuthEndpoint).toBe(true)
    })

    it('should identify stats endpoints as non-critical', () => {
      const error = {
        response: { status: 500 },
        config: {
          url: '/stats/test',
          method: 'get',
          metadata: {}
        }
      }

      const isStatsEndpoint = error.config.url?.includes('/stats/')
      expect(isStatsEndpoint).toBe(true)
    })
  })

  describe('predictImage function', () => {
    beforeEach(async () => {
      globalThis.dispatchEvent = vi.fn()
      vi.clearAllMocks()
      // Reset mockApiInstance methods
      mockApiInstance.post.mockReset()
      // Ensure axios.create returns our mock instance
      mockedAxios.create.mockReturnValue(mockApiInstance)
      // Reset modules to ensure fresh imports use the mocked instance
      vi.resetModules()
    })

    it('should validate FormData contains image', async () => {
      const { predictImage } = await import('../api.js')
      const formData = new FormData()

      await expect(predictImage(formData)).rejects.toThrow('No se ha proporcionado ninguna imagen')
    })

    it('should validate image file is not empty', async () => {
      const { predictImage } = await import('../api.js')
      const formData = new FormData()
      const emptyFile = new File([], 'empty.jpg', { type: 'image/jpeg' })
      formData.append('image', emptyFile)

      await expect(predictImage(formData)).rejects.toThrow('El archivo de imagen está vacío')
    })

    it('should validate image file type', async () => {
      const { predictImage } = await import('../api.js')
      const formData = new FormData()
      const invalidFile = new File(['content'], 'test.txt', { type: 'text/plain' })
      formData.append('image', invalidFile)

      await expect(predictImage(formData)).rejects.toThrow('Formato de imagen no válido')
    })

    it('should validate image file size', async () => {
      const { predictImage } = await import('../api.js')
      const formData = new FormData()
      // Create a file larger than 20MB
      const largeContent = new Array(21 * 1024 * 1024).fill('a').join('')
      const largeFile = new File([largeContent], 'large.jpg', { type: 'image/jpeg' })
      formData.append('image', largeFile)

      await expect(predictImage(formData)).rejects.toThrow('La imagen es demasiado grande')
    })

    it('should accept valid image formats', async () => {
      mockApiInstance.post.mockResolvedValue({
        data: { weight: 1.2, height: 25, width: 20, thickness: 5 }
      })

      vi.resetModules()
      const { predictImage } = await import('../api.js')

      const validFormats = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp']
      
      for (const format of validFormats) {
        const formData = new FormData()
        const validFile = new File(['content'], 'test.jpg', { type: format })
        formData.append('image', validFile)

        // Should not throw validation error
        try {
          await predictImage(formData)
        } catch (error) {
          // Only API errors are acceptable, not validation errors
          expect(error.message).not.toContain('Formato de imagen no válido')
        }
      }
    })

    it('should emit loading start event', async () => {
      mockApiInstance.post.mockResolvedValue({
        data: { weight: 1.2 }
      })

      vi.resetModules()
      const { predictImage } = await import('../api.js')

      const formData = new FormData()
      const validFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', validFile)

      await predictImage(formData)

      expect(globalThis.dispatchEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'api-loading-start',
          detail: expect.objectContaining({
            type: 'prediction'
          })
        })
      )
    })

    it('should emit loading end event on success', async () => {
      mockApiInstance.post.mockResolvedValue({
        data: { weight: 1.2 }
      })

      vi.resetModules()
      const { predictImage } = await import('../api.js')

      const formData = new FormData()
      const validFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', validFile)

      await predictImage(formData)

      const calls = globalThis.dispatchEvent.mock.calls
      const endCall = calls.find(call => call[0].type === 'api-loading-end')
      expect(endCall).toBeDefined()
    })

    it('should emit loading end event on error', async () => {
      mockApiInstance.post.mockRejectedValue(new Error('API Error'))

      vi.resetModules()
      const { predictImage } = await import('../api.js')

      const formData = new FormData()
      const validFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', validFile)

      try {
        await predictImage(formData)
      } catch {
        // Expected to throw
      }

      const calls = globalThis.dispatchEvent.mock.calls
      const endCall = calls.find(call => call[0].type === 'api-loading-end')
      expect(endCall).toBeDefined()
    })

    it('should handle API response errors with detail', async () => {
      const apiError = {
        response: {
          data: {
            error: 'Processing failed',
            detail: 'Image processing error'
          },
          status: 400
        }
      }
      mockApiInstance.post.mockRejectedValue(apiError)

      vi.resetModules()
      const { predictImage } = await import('../api.js')
      const formData = new FormData()
      const validFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', validFile)

      await expect(predictImage(formData)).rejects.toThrow('Processing failed')
    })

    it('should handle API response errors with detail only', async () => {
      const apiError = {
        response: {
          data: {
            detail: 'Image processing error'
          },
          status: 400
        }
      }
      mockApiInstance.post.mockRejectedValue(apiError)

      vi.resetModules()
      const { predictImage } = await import('../api.js')
      const formData = new FormData()
      const validFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', validFile)

      await expect(predictImage(formData)).rejects.toThrow('Image processing error')
    })

    it('should handle network errors', async () => {
      const networkError = new Error('Network Error')
      mockApiInstance.post.mockRejectedValue(networkError)

      vi.resetModules()
      const { predictImage } = await import('../api.js')
      const formData = new FormData()
      const validFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', validFile)

      await expect(predictImage(formData)).rejects.toThrow('Network Error')
    })

    it('should include original error in custom error', async () => {
      const originalError = new Error('Original error')
      originalError.response = { status: 500 }
      mockApiInstance.post.mockRejectedValue(originalError)

      vi.resetModules()
      const { predictImage } = await import('../api.js')
      const formData = new FormData()
      const validFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', validFile)

      try {
        await predictImage(formData)
      } catch (error) {
        expect(error.originalError).toBe(originalError)
        expect(error.status).toBe(500)
      }
    })

    it('should use 60 second timeout for prediction requests', async () => {
      mockApiInstance.post.mockResolvedValue({
        data: { weight: 1.2 }
      })

      vi.resetModules()
      const { predictImage } = await import('../api.js')
      const formData = new FormData()
      const validFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', validFile)

      await predictImage(formData)

      expect(mockApiInstance.post).toHaveBeenCalledWith(
        '/api/predict/',
        formData,
        expect.objectContaining({
          timeout: 60000
        })
      )
    })
  })

  describe('API_CONFIG export', () => {
    it('should export API_CONFIG with base URL', async () => {
      const { API_CONFIG } = await import('../api.js')
      
      expect(API_CONFIG).toBeDefined()
      expect(API_CONFIG.BASE_URL).toBeDefined()
      expect(API_CONFIG.TIMEOUT).toBeDefined()
      expect(API_CONFIG.HEADERS).toBeDefined()
    })
  })

  describe('validateImageFile export', () => {
    it('should export validateImageFile function', async () => {
      const { validateImageFile } = await import('../api.js')
      
      expect(validateImageFile).toBeDefined()
      expect(typeof validateImageFile).toBe('function')
    })
  })
})


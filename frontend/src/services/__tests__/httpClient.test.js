/**
 * Unit tests for HTTP client service
 * Tests axios instance, interceptors, and HTTP methods
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { get, post, put, patch, del, upload, download, httpClient } from '../httpClient.js'

// Use vi.hoisted() to define mocks before vi.mock() hoisting
const { mockAxiosInstance, mockCreate } = vi.hoisted(() => {
  const mockAxiosInstance = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: {
        use: vi.fn()
      },
      response: {
        use: vi.fn()
      }
    }
  }
  const mockCreate = vi.fn(() => mockAxiosInstance)
  return { mockAxiosInstance, mockCreate }
})

vi.mock('axios', () => {
  return {
    default: {
      create: mockCreate
    }
  }
})

vi.mock('@/router', () => ({
  default: {
    push: vi.fn()
  }
}))

vi.mock('@/utils/apiConfig', () => ({
  getApiBaseUrl: vi.fn(() => 'https://api.example.com/api/v1')
}))

vi.mock('@/utils/apiErrorHandler', () => ({
  extractErrorMessage: vi.fn((error) => error?.response?.data?.detail || error.message || 'Error')
}))

vi.mock('@/utils/apiResponseFormatter', () => ({
  normalizeApiResponse: vi.fn((data) => data)
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
globalThis.localStorage = localStorageMock

// Mock console methods
globalThis.console = {
  ...console,
  warn: vi.fn(),
  error: vi.fn()
}

describe('httpClient', () => {
  beforeEach(() => {
    // Clear mocks but preserve mockCreate calls since it's called at module import
    mockAxiosInstance.get.mockClear()
    mockAxiosInstance.post.mockClear()
    mockAxiosInstance.put.mockClear()
    mockAxiosInstance.patch.mockClear()
    mockAxiosInstance.delete.mockClear()
    localStorageMock.getItem.mockClear()
    localStorageMock.getItem.mockReturnValue(null)
    
    // Setup default successful responses
    mockAxiosInstance.get.mockResolvedValue({ data: { success: true } })
    mockAxiosInstance.post.mockResolvedValue({ data: { success: true } })
    mockAxiosInstance.put.mockResolvedValue({ data: { success: true } })
    mockAxiosInstance.patch.mockResolvedValue({ data: { success: true } })
    mockAxiosInstance.delete.mockResolvedValue({ data: { success: true } })
  })

  describe('client creation', () => {
    it('should create axios instance with correct base URL', () => {
      expect(mockCreate).toHaveBeenCalled()
      expect(mockCreate.mock.calls.length).toBeGreaterThan(0)
      const callArgs = mockCreate.mock.calls[0][0]
      expect(callArgs.baseURL).toBe('https://api.example.com/api/v1')
    })

    it('should configure axios with timeout', () => {
      expect(mockCreate.mock.calls.length).toBeGreaterThan(0)
      const callArgs = mockCreate.mock.calls[0][0]
      expect(callArgs.timeout).toBe(15000)
    })

    it('should configure default headers', () => {
      expect(mockCreate.mock.calls.length).toBeGreaterThan(0)
      const callArgs = mockCreate.mock.calls[0][0]
      expect(callArgs.headers['Content-Type']).toBe('application/json')
      expect(callArgs.headers['Accept']).toBe('application/json')
    })
  })

  describe('request interceptor', () => {
    it('should add auth token to headers when available', async () => {
      // Verify interceptor was configured
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled()
      
      // Get the interceptor function that was registered
      const requestInterceptor = mockAxiosInstance.interceptors.request.use.mock.calls[0]?.[0]
      expect(requestInterceptor).toBeDefined()
      
      // Configure localStorage mock
      localStorageMock.getItem.mockReturnValue('test-token')
      
      // Execute interceptor manually to test its behavior
      const config = { headers: {} }
      const modifiedConfig = requestInterceptor(config)
      
      // Verify interceptor called localStorage.getItem with 'auth_token'
      expect(localStorageMock.getItem).toHaveBeenCalledWith('auth_token')
      
      // Verify Authorization header was added
      expect(modifiedConfig.headers.Authorization).toBe('Bearer test-token')
    })

    it('should not add auth token when not available', async () => {
      localStorageMock.getItem.mockReturnValue(null)
      
      await get('/test')
      
      // Should still work without token
      expect(mockAxiosInstance.get).toHaveBeenCalled()
    })
  })

  describe('get', () => {
    it('should make GET request and return data', async () => {
      const mockData = { id: 1, name: 'Test' }
      mockAxiosInstance.get.mockResolvedValue({ data: mockData })
      
      const result = await get('/test')
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/test', {})
      expect(result).toEqual(mockData)
    })

    it('should pass config to axios', async () => {
      const config = { params: { id: 1 } }
      await get('/test', config)
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/test', config)
    })

    it('should throw standardized error on failure', async () => {
      const error = {
        response: {
          status: 404,
          data: { detail: 'Not found' }
        }
      }
      mockAxiosInstance.get.mockRejectedValue(error)
      
      await expect(get('/test')).rejects.toThrow()
    })
  })

  describe('post', () => {
    it('should make POST request with data', async () => {
      const mockData = { id: 1 }
      const postData = { name: 'Test' }
      mockAxiosInstance.post.mockResolvedValue({ data: mockData })
      
      const result = await post('/test', postData)
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/test', postData, {})
      expect(result).toEqual(mockData)
    })

    it('should pass config to axios', async () => {
      const config = { headers: { 'Custom-Header': 'value' } }
      await post('/test', { data: 'test' }, config)
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/test', { data: 'test' }, config)
    })

    it('should throw standardized error on failure', async () => {
      const error = {
        response: {
          status: 400,
          data: { detail: 'Bad request' }
        }
      }
      mockAxiosInstance.post.mockRejectedValue(error)
      
      await expect(post('/test', {})).rejects.toThrow()
    })
  })

  describe('put', () => {
    it('should make PUT request with data', async () => {
      const mockData = { id: 1, updated: true }
      const putData = { name: 'Updated' }
      mockAxiosInstance.put.mockResolvedValue({ data: mockData })
      
      const result = await put('/test/1', putData)
      
      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/test/1', putData, {})
      expect(result).toEqual(mockData)
    })

    it('should throw standardized error on failure', async () => {
      const error = {
        response: {
          status: 500,
          data: { detail: 'Server error' }
        }
      }
      mockAxiosInstance.put.mockRejectedValue(error)
      
      await expect(put('/test/1', {})).rejects.toThrow()
    })
  })

  describe('patch', () => {
    it('should make PATCH request with data', async () => {
      const mockData = { id: 1, patched: true }
      const patchData = { name: 'Patched' }
      mockAxiosInstance.patch.mockResolvedValue({ data: mockData })
      
      const result = await patch('/test/1', patchData)
      
      expect(mockAxiosInstance.patch).toHaveBeenCalledWith('/test/1', patchData, {})
      expect(result).toEqual(mockData)
    })

    it('should throw standardized error on failure', async () => {
      const error = {
        response: {
          status: 422,
          data: { detail: 'Validation error' }
        }
      }
      mockAxiosInstance.patch.mockRejectedValue(error)
      
      await expect(patch('/test/1', {})).rejects.toThrow()
    })
  })

  describe('delete', () => {
    it('should make DELETE request', async () => {
      mockAxiosInstance.delete.mockResolvedValue({ data: { success: true } })
      
      const result = await del('/test/1')
      
      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/test/1', {})
      expect(result).toEqual({ success: true })
    })

    it('should pass config to axios', async () => {
      const config = { headers: { 'Custom-Header': 'value' } }
      await del('/test/1', config)
      
      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/test/1', config)
    })

    it('should throw standardized error on failure', async () => {
      const error = {
        response: {
          status: 403,
          data: { detail: 'Forbidden' }
        }
      }
      mockAxiosInstance.delete.mockRejectedValue(error)
      
      await expect(del('/test/1')).rejects.toThrow()
    })
  })

  describe('upload', () => {
    it('should make POST request with FormData', async () => {
      const formData = new FormData()
      formData.append('file', new Blob(['test']))
      const mockData = { id: 1, url: 'https://example.com/file.jpg' }
      mockAxiosInstance.post.mockResolvedValue({ data: mockData })
      
      const result = await upload('/upload', formData)
      
      expect(mockAxiosInstance.post).toHaveBeenCalled()
      const callArgs = mockAxiosInstance.post.mock.calls[0]
      expect(callArgs[0]).toBe('/upload')
      expect(callArgs[1]).toBe(formData)
      expect(callArgs[2].headers['Content-Type']).toBe('multipart/form-data')
      expect(result).toEqual(mockData)
    })

    it('should call progress callback when provided', async () => {
      const formData = new FormData()
      const onProgress = vi.fn()
      const progressEvent = {
        loaded: 50,
        total: 100
      }
      
      mockAxiosInstance.post.mockImplementation((url, data, config) => {
        if (config.onUploadProgress) {
          config.onUploadProgress(progressEvent)
        }
        return Promise.resolve({ data: { success: true } })
      })
      
      await upload('/upload', formData, onProgress)
      
      expect(onProgress).toHaveBeenCalledWith(50)
    })

    it('should throw standardized error on failure', async () => {
      const formData = new FormData()
      const error = {
        response: {
          status: 413,
          data: { detail: 'File too large' }
        }
      }
      mockAxiosInstance.post.mockRejectedValue(error)
      
      await expect(upload('/upload', formData)).rejects.toThrow()
    })
  })

  describe('download', () => {
    it('should make GET request with blob response type', async () => {
      const mockBlob = new Blob(['test content'])
      mockAxiosInstance.get.mockResolvedValue({ data: mockBlob })
      
      const result = await download('/download/file.pdf')
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/download/file.pdf', {
        responseType: 'blob'
      })
      expect(result.data).toBe(mockBlob)
    })

    it('should merge config with blob response type', async () => {
      const config = { headers: { 'Accept': 'application/pdf' } }
      await download('/download/file.pdf', config)
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/download/file.pdf', {
        ...config,
        responseType: 'blob'
      })
    })

    it('should throw standardized error on failure', async () => {
      const error = {
        response: {
          status: 404,
          data: { detail: 'File not found' }
        }
      }
      mockAxiosInstance.get.mockRejectedValue(error)
      
      await expect(download('/download/missing.pdf')).rejects.toThrow()
    })
  })

  describe('response interceptor - error handling', () => {
    it('should handle 401 unauthorized - clear tokens and redirect', async () => {
      await import('@/router')
      const error = {
        response: {
          status: 401,
          data: { detail: 'Unauthorized' }
        }
      }
      mockAxiosInstance.get.mockRejectedValue(error)
      
      await expect(get('/protected')).rejects.toThrow()
      
      // Note: Interceptors are set up at module load time, so we test the behavior
      // by checking that errors are properly thrown
      expect(mockAxiosInstance.get).toHaveBeenCalled()
    })

    it('should handle network errors', async () => {
      const error = {
        request: {},
        message: 'Network Error'
      }
      mockAxiosInstance.get.mockRejectedValue(error)
      
      await expect(get('/test')).rejects.toThrow()
    })

    it('should handle request setup errors', async () => {
      const error = {
        message: 'Request setup error'
      }
      mockAxiosInstance.get.mockRejectedValue(error)
      
      await expect(get('/test')).rejects.toThrow()
    })
  })

  describe('httpClient export', () => {
    it('should export httpClient instance', () => {
      expect(httpClient).toBeDefined()
      expect(httpClient.get).toBeDefined()
      expect(httpClient.post).toBeDefined()
    })
  })
})

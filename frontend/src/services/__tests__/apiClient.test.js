/**
 * Unit tests for API client service
 * Tests unified API client methods and error handling
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  apiGet,
  apiPost,
  apiPut,
  apiPatch,
  apiDelete,
  fetchGet,
  fetchPost,
  extractErrorMessage,
  extractValidationErrors,
  makePaginatedRequest,
  buildQueryParams,
  getCommonHeaders
} from '../apiClient.js'
import api from '../api.js'

// Mock dependencies
vi.mock('../api.js', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  }
}))

vi.mock('@/utils/apiConfig', () => ({
  getApiBaseUrlWithoutPath: vi.fn(() => 'https://api.example.com')
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
globalThis.localStorage = localStorageMock

// Mock fetch
globalThis.fetch = vi.fn()

// Mock fetch
globalThis.fetch = vi.fn()

describe('apiClient', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
    
    // Setup default successful responses
    api.get.mockResolvedValue({ data: { success: true } })
    api.post.mockResolvedValue({ data: { success: true } })
    api.put.mockResolvedValue({ data: { success: true } })
    api.patch.mockResolvedValue({ data: { success: true } })
    api.delete.mockResolvedValue({ data: { success: true } })
    
    // Setup default fetch responses
    globalThis.fetch.mockResolvedValue({
      ok: true,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: vi.fn().mockResolvedValue({ success: true }),
      text: vi.fn().mockResolvedValue('text response')
    })
  })

  describe('apiGet', () => {
    it('should make GET request and return data', async () => {
      const mockData = { id: 1, name: 'Test' }
      api.get.mockResolvedValue({ data: mockData })
      
      const result = await apiGet('/test')
      
      expect(api.get).toHaveBeenCalledWith('/test', { params: {} })
      expect(result).toEqual(mockData)
    })

    it('should pass params to axios', async () => {
      const params = { page: 1, limit: 10 }
      await apiGet('/test', params)
      
      expect(api.get).toHaveBeenCalledWith('/test', { params })
    })

    it('should pass additional options to axios', async () => {
      const params = { page: 1 }
      const options = { headers: { 'Custom-Header': 'value' } }
      await apiGet('/test', params, options)
      
      expect(api.get).toHaveBeenCalledWith('/test', { params, ...options })
    })

    it('should log error and throw on failure', async () => {
      const error = new Error('Network error')
      api.get.mockRejectedValue(error)
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      await expect(apiGet('/test')).rejects.toThrow('Network error')
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining('[apiClient] GET /test error:'),
        error
      )
      consoleErrorSpy.mockRestore()
    })
  })

  describe('apiPost', () => {
    it('should make POST request with data', async () => {
      const mockData = { id: 1 }
      const postData = { name: 'Test' }
      api.post.mockResolvedValue({ data: mockData })
      
      const result = await apiPost('/test', postData)
      
      expect(api.post).toHaveBeenCalledWith('/test', postData, {})
      expect(result).toEqual(mockData)
    })

    it('should pass options to axios', async () => {
      const options = { headers: { 'Content-Type': 'multipart/form-data' } }
      await apiPost('/test', { data: 'test' }, options)
      
      expect(api.post).toHaveBeenCalledWith('/test', { data: 'test' }, options)
    })

    it('should handle empty data', async () => {
      await apiPost('/test')
      
      expect(api.post).toHaveBeenCalledWith('/test', {}, {})
    })

    it('should log error and throw on failure', async () => {
      const error = new Error('Validation error')
      api.post.mockRejectedValue(error)
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      await expect(apiPost('/test', {})).rejects.toThrow('Validation error')
      expect(consoleErrorSpy).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })
  })

  describe('apiPut', () => {
    it('should make PUT request with data', async () => {
      const mockData = { id: 1, updated: true }
      const putData = { name: 'Updated' }
      api.put.mockResolvedValue({ data: mockData })
      
      const result = await apiPut('/test/1', putData)
      
      expect(api.put).toHaveBeenCalledWith('/test/1', putData, {})
      expect(result).toEqual(mockData)
    })

    it('should pass options to axios', async () => {
      const options = { headers: { 'Custom-Header': 'value' } }
      await apiPut('/test/1', { data: 'test' }, options)
      
      expect(api.put).toHaveBeenCalledWith('/test/1', { data: 'test' }, options)
    })

    it('should log error and throw on failure', async () => {
      const error = new Error('Update error')
      api.put.mockRejectedValue(error)
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      await expect(apiPut('/test/1', {})).rejects.toThrow('Update error')
      expect(consoleErrorSpy).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })
  })

  describe('apiPatch', () => {
    it('should make PATCH request with data', async () => {
      const mockData = { id: 1, patched: true }
      const patchData = { name: 'Patched' }
      api.patch.mockResolvedValue({ data: mockData })
      
      const result = await apiPatch('/test/1', patchData)
      
      expect(api.patch).toHaveBeenCalledWith('/test/1', patchData, {})
      expect(result).toEqual(mockData)
    })

    it('should pass options to axios', async () => {
      const options = { headers: { 'Custom-Header': 'value' } }
      await apiPatch('/test/1', { data: 'test' }, options)
      
      expect(api.patch).toHaveBeenCalledWith('/test/1', { data: 'test' }, options)
    })

    it('should log error and throw on failure', async () => {
      const error = new Error('Patch error')
      api.patch.mockRejectedValue(error)
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      await expect(apiPatch('/test/1', {})).rejects.toThrow('Patch error')
      expect(consoleErrorSpy).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })
  })

  describe('apiDelete', () => {
    it('should make DELETE request', async () => {
      api.delete.mockResolvedValue({ data: { success: true } })
      
      const result = await apiDelete('/test/1')
      
      expect(api.delete).toHaveBeenCalledWith('/test/1', {})
      expect(result).toEqual({ success: true })
    })

    it('should pass options to axios', async () => {
      const options = { headers: { 'Custom-Header': 'value' } }
      await apiDelete('/test/1', options)
      
      expect(api.delete).toHaveBeenCalledWith('/test/1', options)
    })

    it('should log error and throw on failure', async () => {
      const error = new Error('Delete error')
      api.delete.mockRejectedValue(error)
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      await expect(apiDelete('/test/1')).rejects.toThrow('Delete error')
      expect(consoleErrorSpy).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })
  })

  describe('fetchGet', () => {
    it('should make GET request with fetch', async () => {
      const mockData = { id: 1, name: 'Test' }
      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue(mockData)
      })
      
      const result = await fetchGet('/test', { page: 1 })
      
      expect(globalThis.fetch).toHaveBeenCalled()
      const callUrl = globalThis.fetch.mock.calls[0][0]
      expect(callUrl).toContain('/test')
      expect(callUrl).toContain('page=1')
      expect(result).toEqual(mockData)
    })

    it('should handle absolute URLs', async () => {
      const absoluteUrl = 'https://external.com/api/test'
      await fetchGet(absoluteUrl)
      
      const callUrl = globalThis.fetch.mock.calls[0][0]
      expect(callUrl).toBe(absoluteUrl + '?')
    })

    it('should include auth token in headers when available', async () => {
      localStorageMock.getItem.mockReturnValue('test-token')
      
      await fetchGet('/test')
      
      const fetchCall = globalThis.fetch.mock.calls[0]
      const headers = fetchCall[1].headers
      expect(headers['Authorization']).toBe('Bearer test-token')
    })
  })

  describe('fetchPost', () => {
    it('should make POST request with fetch', async () => {
      const mockData = { id: 1 }
      const postData = { name: 'Test' }
      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue(mockData)
      })
      
      const result = await fetchPost('/test', postData)
      
      expect(globalThis.fetch).toHaveBeenCalled()
      const fetchCall = globalThis.fetch.mock.calls[0]
      expect(fetchCall[0]).toContain('/test')
      expect(fetchCall[1].method).toBe('POST')
      expect(JSON.parse(fetchCall[1].body)).toEqual(postData)
      expect(result).toEqual(mockData)
    })
  })

  describe('extractErrorMessage', () => {
    it('should extract message from response.data', () => {
      const error = {
        response: {
          data: {
            message: 'Error message'
          }
        }
      }
      
      expect(extractErrorMessage(error)).toBe('Error message')
    })

    it('should prioritize error field', () => {
      const error = {
        response: {
          data: {
            error: 'Error field',
            message: 'Message field'
          }
        }
      }
      
      expect(extractErrorMessage(error)).toBe('Error field')
    })

    it('should prioritize detail field', () => {
      const error = {
        response: {
          data: {
            detail: 'Detail message',
            error: 'Error field'
          }
        }
      }
      
      expect(extractErrorMessage(error)).toBe('Detail message')
    })

    it('should use error.message if available', () => {
      const error = {
        message: 'Network error'
      }
      
      expect(extractErrorMessage(error)).toBe('Network error')
    })

    it('should use default message when no error found', () => {
      const error = {}
      
      expect(extractErrorMessage(error, 'Custom default')).toBe('Custom default')
    })
  })

  describe('extractValidationErrors', () => {
    it('should extract validation errors from response.data.details', () => {
      const error = {
        response: {
          data: {
            details: {
              field1: 'Error 1',
              field2: 'Error 2'
            }
          }
        }
      }
      
      expect(extractValidationErrors(error)).toEqual({
        field1: 'Error 1',
        field2: 'Error 2'
      })
    })

    it('should extract validation errors from response.data', () => {
      const error = {
        response: {
          data: {
            field1: 'Error 1',
            field2: 'Error 2'
          }
        }
      }
      
      expect(extractValidationErrors(error)).toEqual({
        field1: 'Error 1',
        field2: 'Error 2'
      })
    })

    it('should return empty object when no validation errors', () => {
      const error = {
        response: {
          data: {
            message: 'General error'
          }
        }
      }
      
      expect(extractValidationErrors(error)).toEqual({})
    })
  })

  describe('makePaginatedRequest', () => {
    it('should add pagination params to request', async () => {
      const requestFn = vi.fn().mockResolvedValue({ results: [] })
      const pagination = {
        currentPage: 2,
        itemsPerPage: 20
      }
      
      await makePaginatedRequest(requestFn, { filter: 'test' }, pagination)
      
      expect(requestFn).toHaveBeenCalledWith({
        filter: 'test',
        page: 2,
        page_size: 20
      })
    })

    it('should use default pagination values', async () => {
      const requestFn = vi.fn().mockResolvedValue({ results: [] })
      
      await makePaginatedRequest(requestFn)
      
      expect(requestFn).toHaveBeenCalledWith({
        page: 1,
        page_size: 10
      })
    })
  })

  describe('buildQueryParams', () => {
    it('should build query params from object', () => {
      const filters = { page: 1, limit: 10, search: 'test' }
      const params = buildQueryParams(filters)
      
      expect(params.get('page')).toBe('1')
      expect(params.get('limit')).toBe('10')
      expect(params.get('search')).toBe('test')
    })

    it('should handle array values', () => {
      const filters = { tags: ['tag1', 'tag2'] }
      const params = buildQueryParams(filters)
      
      expect(params.getAll('tags')).toEqual(['tag1', 'tag2'])
    })

    it('should exclude null, undefined, and empty values', () => {
      const filters = { page: 1, empty: '', nullValue: null, undefinedValue: undefined }
      const params = buildQueryParams(filters)
      
      expect(params.get('page')).toBe('1')
      expect(params.has('empty')).toBe(false)
      expect(params.has('nullValue')).toBe(false)
      expect(params.has('undefinedValue')).toBe(false)
    })
  })

  describe('getCommonHeaders', () => {
    it('should include Content-Type header', () => {
      const headers = getCommonHeaders()
      
      expect(headers['Content-Type']).toBe('application/json')
    })

    it('should include Authorization header when token exists', () => {
      localStorageMock.getItem.mockReturnValue('test-token')
      
      const headers = getCommonHeaders()
      
      expect(headers['Authorization']).toBe('Bearer test-token')
    })

    it('should not include Authorization header when no token', () => {
      localStorageMock.getItem.mockReturnValue(null)
      
      const headers = getCommonHeaders()
      
      expect(headers).not.toHaveProperty('Authorization')
    })

    it('should check access_token first, then token', () => {
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'access-token'
        if (key === 'token') return 'token-value'
        return null
      })
      
      const headers = getCommonHeaders()
      
      expect(headers['Authorization']).toBe('Bearer access-token')
    })
  })
})


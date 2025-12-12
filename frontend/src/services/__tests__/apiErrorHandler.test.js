/**
 * Unit tests for services/apiErrorHandler
 * Tests error type detection and error message formatting
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  API_ERROR_TYPES,
  getErrorType,
  getErrorMessage,
  getValidationErrors,
  isValidationError,
  isAuthenticationError,
  handleApiError
} from '../apiErrorHandler.js'
import { extractErrorMessage, extractValidationErrors } from '../apiClient.js'
import { logger } from '@/utils/logger'

// Mock dependencies
vi.mock('../apiClient.js', () => ({
  extractErrorMessage: vi.fn((error, defaultMsg) => defaultMsg || 'Error message'),
  extractValidationErrors: vi.fn(() => ({}))
}))

vi.mock('@/utils/logger', () => ({
  logger: {
    error: vi.fn()
  }
}))

describe('services/apiErrorHandler', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('API_ERROR_TYPES', () => {
    it('should export error types constants', () => {
      expect(API_ERROR_TYPES.NETWORK).toBe('network')
      expect(API_ERROR_TYPES.TIMEOUT).toBe('timeout')
      expect(API_ERROR_TYPES.VALIDATION).toBe('validation')
      expect(API_ERROR_TYPES.AUTHENTICATION).toBe('authentication')
      expect(API_ERROR_TYPES.AUTHORIZATION).toBe('authorization')
      expect(API_ERROR_TYPES.NOT_FOUND).toBe('not_found')
      expect(API_ERROR_TYPES.SERVER).toBe('server')
      expect(API_ERROR_TYPES.UNKNOWN).toBe('unknown')
    })
  })

  describe('getErrorType', () => {
    it('should detect network error', () => {
      const error = { message: 'Network Error' }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.NETWORK)
    })

    it('should detect network error with "Failed to fetch"', () => {
      const error = { message: 'Failed to fetch' }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.NETWORK)
    })

    it('should detect timeout error', () => {
      const error = { code: 'ECONNABORTED' }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.TIMEOUT)
    })

    it('should detect timeout error from message', () => {
      const error = { message: 'Request timeout' }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.TIMEOUT)
    })

    it('should detect authentication error', () => {
      const error = { response: { status: 401 } }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.AUTHENTICATION)
    })

    it('should detect authorization error', () => {
      const error = { response: { status: 403 } }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.AUTHORIZATION)
    })

    it('should detect not found error', () => {
      const error = { response: { status: 404 } }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.NOT_FOUND)
    })

    it('should detect validation error with status 422', () => {
      const error = { response: { status: 422 } }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.VALIDATION)
    })

    it('should detect validation error with status 400', () => {
      const error = { response: { status: 400 } }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.VALIDATION)
    })

    it('should detect server error with status 500', () => {
      const error = { response: { status: 500 } }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.SERVER)
    })

    it('should detect server error with status 502', () => {
      const error = { response: { status: 502 } }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.SERVER)
    })

    it('should detect server error with status 503', () => {
      const error = { response: { status: 503 } }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.SERVER)
    })

    it('should detect server error with status 504', () => {
      const error = { response: { status: 504 } }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.SERVER)
    })

    it('should detect validation error from response.data.details', () => {
      const error = { response: { data: { details: {} } } }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.VALIDATION)
    })

    it('should detect validation error from error.data.details', () => {
      const error = { data: { details: {} } }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.VALIDATION)
    })

    it('should return unknown for unrecognized error', () => {
      const error = {}
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.UNKNOWN)
    })

    it('should return unknown for error with status < 500', () => {
      const error = { response: { status: 418 } }
      expect(getErrorType(error)).toBe(API_ERROR_TYPES.UNKNOWN)
    })
  })

  describe('getErrorMessage', () => {
    it('should return network error message', () => {
      const error = { message: 'Network Error' }
      const message = getErrorMessage(error)
      expect(message).toContain('conexión')
    })

    it('should return timeout error message', () => {
      const error = { code: 'ECONNABORTED' }
      const message = getErrorMessage(error)
      expect(message).toContain('tardó demasiado')
    })

    it('should return authentication error message', () => {
      const error = { response: { status: 401 } }
      const message = getErrorMessage(error)
      expect(message).toContain('sesión')
    })

    it('should return authorization error message', () => {
      const error = { response: { status: 403 } }
      const message = getErrorMessage(error)
      expect(message).toContain('permisos')
    })

    it('should return not found error message', () => {
      const error = { response: { status: 404 } }
      const message = getErrorMessage(error)
      expect(message).toContain('no fue encontrado')
    })

    it('should return server error message', () => {
      const error = { response: { status: 500 } }
      const message = getErrorMessage(error)
      expect(message).toContain('servidor')
    })

    it('should return validation error message', () => {
      const error = { response: { status: 422 } }
      getErrorMessage(error)
      expect(extractErrorMessage).toHaveBeenCalled()
    })

    it('should use default message for unknown errors', () => {
      getErrorMessage({}, 'Custom default')
      expect(extractErrorMessage).toHaveBeenCalled()
    })
  })

  describe('getValidationErrors', () => {
    it('should extract validation errors', () => {
      const error = { response: { status: 422 } }
      getValidationErrors(error)
      expect(extractValidationErrors).toHaveBeenCalledWith(error)
    })
  })

  describe('isValidationError', () => {
    it('should return true for validation error', () => {
      const error = { response: { status: 422 } }
      expect(isValidationError(error)).toBe(true)
    })

    it('should return false for non-validation error', () => {
      const error = { response: { status: 500 } }
      expect(isValidationError(error)).toBe(false)
    })
  })

  describe('isAuthenticationError', () => {
    it('should return true for authentication error', () => {
      const error = { response: { status: 401 } }
      expect(isAuthenticationError(error)).toBe(true)
    })

    it('should return false for non-authentication error', () => {
      const error = { response: { status: 403 } }
      expect(isAuthenticationError(error)).toBe(false)
    })
  })

  describe('handleApiError', () => {
    it('should handle error and return error info', () => {
      const error = { response: { status: 500 } }
      const errorInfo = handleApiError(error)
      
      expect(errorInfo).toHaveProperty('type')
      expect(errorInfo).toHaveProperty('message')
      expect(errorInfo).toHaveProperty('originalError')
      expect(errorInfo.type).toBe(API_ERROR_TYPES.SERVER)
    })

    it('should include validation errors for validation errors', () => {
      const error = { response: { status: 422, data: { details: { field: ['Error'] } } } }
      extractValidationErrors.mockReturnValue({ field: ['Error'] })
      const errorInfo = handleApiError(error)
      
      expect(errorInfo.validationErrors).toEqual({ field: ['Error'] })
    })

    it('should not include validation errors for non-validation errors', () => {
      const error = { response: { status: 500 } }
      const errorInfo = handleApiError(error)
      
      expect(errorInfo.validationErrors).toBe(null)
    })

    it('should log error by default', () => {
      const error = { response: { status: 500 } }
      handleApiError(error)
      
      expect(logger.error).toHaveBeenCalled()
    })

    it('should not log error when logError is false', () => {
      const error = { response: { status: 500 } }
      handleApiError(error, { logError: false })
      
      expect(logger.error).not.toHaveBeenCalled()
    })

    it('should call onError callback if provided', () => {
      const error = { response: { status: 500 } }
      const onError = vi.fn()
      handleApiError(error, { onError })
      
      expect(onError).toHaveBeenCalled()
    })

    it('should not call onError callback if not a function', () => {
      const error = { response: { status: 500 } }
      const onError = 'not a function'
      
      expect(() => handleApiError(error, { onError })).not.toThrow()
    })

    it('should handle error without response', () => {
      const error = { message: 'Network Error' }
      const errorInfo = handleApiError(error)
      
      expect(errorInfo.type).toBe(API_ERROR_TYPES.NETWORK)
    })
  })
})


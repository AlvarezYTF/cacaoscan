/**
 * Unit tests for API error handler utility functions
 * Pure functions with minimal dependencies - deterministic tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  extractErrorMessage,
  formatApiResponse,
  handleApiError,
  createErrorResponse
} from '../apiErrorHandler.js'

describe('apiErrorHandler', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    console.error = vi.fn()
  })

  describe('extractErrorMessage', () => {
    it('should extract error from response.data.detail', () => {
      const error = {
        response: {
          data: {
            detail: 'Error detail message'
          }
        }
      }
      expect(extractErrorMessage(error)).toBe('Error detail message')
    })

    it('should extract error from response.data.error', () => {
      const error = {
        response: {
          data: {
            error: 'Error message'
          }
        }
      }
      expect(extractErrorMessage(error)).toBe('Error message')
    })

    it('should extract error from response.data.message', () => {
      const error = {
        response: {
          data: {
            message: 'Error message'
          }
        }
      }
      expect(extractErrorMessage(error)).toBe('Error message')
    })

    it('should extract error from error.message', () => {
      const error = {
        message: 'Error message'
      }
      expect(extractErrorMessage(error)).toBe('Error message')
    })

    it('should return default message when no error found', () => {
      const error = {}
      expect(extractErrorMessage(error)).toBe('Error inesperado')
    })

    it('should return custom default message', () => {
      const error = {}
      expect(extractErrorMessage(error, 'Custom error')).toBe('Custom error')
    })

    it('should prioritize detail over error', () => {
      const error = {
        response: {
          data: {
            detail: 'Detail message',
            error: 'Error message'
          }
        }
      }
      expect(extractErrorMessage(error)).toBe('Detail message')
    })

    it('should prioritize error over message', () => {
      const error = {
        response: {
          data: {
            error: 'Error message',
            message: 'Message'
          }
        }
      }
      expect(extractErrorMessage(error)).toBe('Error message')
    })

    it('should handle null error', () => {
      expect(extractErrorMessage(null)).toBe('Error inesperado')
    })

    it('should handle undefined error', () => {
      expect(extractErrorMessage(undefined)).toBe('Error inesperado')
    })

    it('should handle error without response', () => {
      const error = {
        message: 'Network error'
      }
      expect(extractErrorMessage(error)).toBe('Network error')
    })
  })

  describe('formatApiResponse', () => {
    it('should return response as-is when wrapInSuccess is false', () => {
      const response = { data: 'test' }
      expect(formatApiResponse(response, false)).toBe(response)
    })

    it('should wrap response in success object when wrapInSuccess is true', () => {
      const response = { data: 'test' }
      const result = formatApiResponse(response, true)
      expect(result).toEqual({
        success: true,
        data: { data: 'test' }
      })
    })

    it('should wrap response when wrapInSuccess is not provided', () => {
      const response = { data: 'test' }
      const result = formatApiResponse(response)
      expect(result).toBe(response)
    })
  })

  describe('handleApiError', () => {
    it('should create error response with extracted message', () => {
      const error = {
        response: {
          data: {
            detail: 'Error detail'
          },
          status: 400,
          statusText: 'Bad Request'
        }
      }
      const result = handleApiError(error)
      expect(result.success).toBe(false)
      expect(result.error).toBe('Error detail')
      expect(result.status).toBe(400)
      expect(result.statusText).toBe('Bad Request')
      expect(result.originalError).toBe(error)
    })

    it('should log error with context', () => {
      const error = {
        response: {
          data: {
            detail: 'Error detail'
          }
        }
      }
      handleApiError(error, 'TestContext')
      expect(console.error).toHaveBeenCalledWith(
        expect.stringContaining('[TestContext]'),
        'Error detail',
        error
      )
    })

    it('should log error without context', () => {
      const error = {
        response: {
          data: {
            detail: 'Error detail'
          }
        }
      }
      handleApiError(error)
      expect(console.error).toHaveBeenCalledWith(
        '❌ API Error:',
        'Error detail',
        error
      )
    })

    it('should use default message when no error message found', () => {
      const error = {}
      const result = handleApiError(error, '', 'Custom default')
      expect(result.error).toBe('Custom default')
    })

    it('should handle error without response', () => {
      const error = {
        message: 'Network error'
      }
      const result = handleApiError(error)
      expect(result.success).toBe(false)
      expect(result.error).toBe('Network error')
      expect(result.status).toBeUndefined()
      expect(result.statusText).toBeUndefined()
    })

    it('should include original error in response', () => {
      const error = {
        response: {
          data: {
            detail: 'Error'
          }
        }
      }
      const result = handleApiError(error)
      expect(result.originalError).toBe(error)
    })
  })

  describe('createErrorResponse', () => {
    it('should create error response with message', () => {
      const result = createErrorResponse('Error message')
      expect(result).toEqual({
        success: false,
        error: 'Error message',
        status: null,
        originalError: null
      })
    })

    it('should create error response with status', () => {
      const result = createErrorResponse('Error message', 404)
      expect(result).toEqual({
        success: false,
        error: 'Error message',
        status: 404,
        originalError: null
      })
    })

    it('should create error response with original error', () => {
      const originalError = new Error('Original')
      const result = createErrorResponse('Error message', 500, originalError)
      expect(result).toEqual({
        success: false,
        error: 'Error message',
        status: 500,
        originalError
      })
    })

    it('should create minimal error response', () => {
      const result = createErrorResponse('Error')
      expect(result.success).toBe(false)
      expect(result.error).toBe('Error')
      expect(result.status).toBe(null)
      expect(result.originalError).toBe(null)
    })
  })
})


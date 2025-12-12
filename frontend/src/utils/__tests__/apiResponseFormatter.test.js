/**
 * Unit tests for API response formatter utility functions
 */

import { describe, it, expect } from 'vitest'
import {
  formatSuccessResponse,
  formatErrorResponse,
  normalizeApiResponse,
  normalizeResponse
} from '../apiResponseFormatter.js'

describe('apiResponseFormatter', () => {
  describe('formatSuccessResponse', () => {
    it('should format success response with data', () => {
      const data = { id: 1, name: 'Test' }
      const result = formatSuccessResponse(data)
      
      expect(result.success).toBe(true)
      expect(result.data).toEqual(data)
    })

    it('should include message when provided', () => {
      const data = { id: 1 }
      const message = 'Operation successful'
      const result = formatSuccessResponse(data, message)
      
      expect(result.success).toBe(true)
      expect(result.data).toEqual(data)
      expect(result.message).toBe(message)
    })

    it('should not include message when not provided', () => {
      const data = { id: 1 }
      const result = formatSuccessResponse(data)
      
      expect(result.success).toBe(true)
      expect(result).not.toHaveProperty('message')
    })

    it('should handle null data', () => {
      const result = formatSuccessResponse(null)
      
      expect(result.success).toBe(true)
      expect(result.data).toBe(null)
    })
  })

  describe('formatErrorResponse', () => {
    it('should format error response', () => {
      const error = 'Something went wrong'
      const result = formatErrorResponse(error)
      
      expect(result.success).toBe(false)
      expect(result.error).toBe(error)
    })

    it('should include details when provided', () => {
      const error = 'Validation failed'
      const details = { field: 'email', reason: 'Invalid format' }
      const result = formatErrorResponse(error, details)
      
      expect(result.success).toBe(false)
      expect(result.error).toBe(error)
      expect(result.details).toEqual(details)
    })

    it('should not include details when not provided', () => {
      const error = 'Error occurred'
      const result = formatErrorResponse(error)
      
      expect(result.success).toBe(false)
      expect(result).not.toHaveProperty('details')
    })
  })

  describe('normalizeApiResponse', () => {
    it('should return response as is if already normalized', () => {
      const response = {
        success: true,
        data: { id: 1 }
      }
      
      const result = normalizeApiResponse(response)
      
      expect(result).toEqual(response)
    })

    it('should wrap response when alwaysWrap is true', () => {
      const data = { id: 1, name: 'Test' }
      const result = normalizeApiResponse(data, true)
      
      expect(result.success).toBe(true)
      expect(result.data).toEqual(data)
    })

    it('should return as is when alwaysWrap is false', () => {
      const data = { id: 1, name: 'Test' }
      const result = normalizeApiResponse(data, false)
      
      expect(result).toEqual(data)
    })

    it('should handle error response format', () => {
      const response = {
        success: false,
        error: 'Error message'
      }
      
      const result = normalizeApiResponse(response)
      
      expect(result).toEqual(response)
    })
  })

  describe('normalizeResponse', () => {
    it('should extract results from paginated response', () => {
      const paginatedData = {
        results: [{ id: 1 }, { id: 2 }],
        count: 2,
        next: null,
        previous: null
      }
      
      const result = normalizeResponse(paginatedData)
      
      expect(result).toEqual([{ id: 1 }, { id: 2 }])
    })

    it('should return array as is', () => {
      const arrayData = [{ id: 1 }, { id: 2 }]
      const result = normalizeResponse(arrayData)
      
      expect(result).toEqual(arrayData)
    })

    it('should return empty array for invalid input', () => {
      expect(normalizeResponse(null)).toEqual([])
      expect(normalizeResponse(undefined)).toEqual([])
      expect(normalizeResponse({})).toEqual([])
      expect(normalizeResponse('string')).toEqual([])
    })

    it('should handle empty results array', () => {
      const paginatedData = {
        results: [],
        count: 0
      }
      
      const result = normalizeResponse(paginatedData)
      
      expect(result).toEqual([])
    })
  })
})


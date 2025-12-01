import { describe, it, expect } from 'vitest'
import { normalizeResponse } from '../apiResponse'

describe('apiResponse', () => {
  describe('normalizeResponse', () => {
    it('should return results array from paginated response', () => {
      const data = {
        results: [
          { id: 1, name: 'Item 1' },
          { id: 2, name: 'Item 2' }
        ],
        count: 2
      }

      const result = normalizeResponse(data)

      expect(result).toEqual(data.results)
      expect(result).toHaveLength(2)
    })

    it('should return array directly if data is already an array', () => {
      const data = [
        { id: 1, name: 'Item 1' },
        { id: 2, name: 'Item 2' }
      ]

      const result = normalizeResponse(data)

      expect(result).toEqual(data)
      expect(Array.isArray(result)).toBe(true)
    })

    it('should return empty array if data is not array and has no results', () => {
      const data = { count: 0 }

      const result = normalizeResponse(data)

      expect(result).toEqual([])
      expect(Array.isArray(result)).toBe(true)
    })

    it('should return empty array if data is null', () => {
      const result = normalizeResponse(null)

      expect(result).toEqual([])
    })

    it('should return empty array if data is undefined', () => {
      const result = normalizeResponse(undefined)

      expect(result).toEqual([])
    })

    it('should return empty array if data is empty object', () => {
      const result = normalizeResponse({})

      expect(result).toEqual([])
    })
  })
})


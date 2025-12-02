/**
 * Unit tests for ID generator utility
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { generateSecureId } from '../idGenerator.js'

describe('idGenerator', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset counter
    generateSecureId.counter = 0
  })

  describe('generateSecureId', () => {
    it('should generate id with default prefix', () => {
      const id = generateSecureId()
      expect(id).toMatch(/^id-/)
      expect(typeof id).toBe('string')
    })

    it('should generate id with custom prefix', () => {
      const id = generateSecureId('test')
      expect(id).toMatch(/^test-/)
    })

    it('should generate unique ids', () => {
      const id1 = generateSecureId()
      const id2 = generateSecureId()
      expect(id1).not.toBe(id2)
    })

    it('should generate ids with correct format', () => {
      const id = generateSecureId('custom')
      expect(id).toMatch(/^custom-[\w-]+$/)
    })

    it('should generate different ids for different prefixes', () => {
      const id1 = generateSecureId('prefix1')
      const id2 = generateSecureId('prefix2')
      expect(id1).not.toBe(id2)
      expect(id1.startsWith('prefix1-')).toBe(true)
      expect(id2.startsWith('prefix2-')).toBe(true)
    })

    it('should use crypto.getRandomValues when available', () => {
      const mockCrypto = {
        getRandomValues: vi.fn((arr) => {
          for (let i = 0; i < arr.length; i++) {
            arr[i] = Math.floor(Math.random() * 256)
          }
          return arr
        })
      }
      
      const originalCrypto = globalThis.crypto
      vi.stubGlobal('crypto', mockCrypto)
      
      const id = generateSecureId('test')
      
      expect(mockCrypto.getRandomValues).toHaveBeenCalled()
      expect(id).toMatch(/^test-/)
      
      vi.unstubAllGlobals()
      if (originalCrypto) {
        vi.stubGlobal('crypto', originalCrypto)
      }
    })

    it('should fallback when crypto is not available', () => {
      const originalCrypto = globalThis.crypto
      vi.stubGlobal('crypto', undefined)
      
      const id = generateSecureId('fallback')
      
      expect(id).toMatch(/^fallback-/)
      expect(id).toContain('-')
      
      vi.unstubAllGlobals()
      if (originalCrypto) {
        vi.stubGlobal('crypto', originalCrypto)
      }
    })
  })
})


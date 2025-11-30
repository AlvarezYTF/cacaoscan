import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  getApiBaseUrl,
  getApiBaseUrlWithoutPath,
  getApiBaseUrlWithPath,
  isDevelopment,
  isProduction,
  API_CONFIG
} from '../apiConfig'

describe('apiConfig', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset globalThis
    delete globalThis.__API_BASE_URL__
    delete globalThis.location
  })

  describe('getApiBaseUrl', () => {
    it('should use runtime URL if available', () => {
      globalThis.__API_BASE_URL__ = 'https://api.example.com/api/v1'
      globalThis.location = { hostname: 'example.com' }

      const url = getApiBaseUrl()

      expect(url).toBe('https://api.example.com/api/v1')
    })

    it('should use build-time variable if runtime URL not available', () => {
      const originalEnv = import.meta.env
      import.meta.env = {
        ...originalEnv,
        VITE_API_BASE_URL: 'https://build-time-api.com/api/v1'
      }

      const url = getApiBaseUrl()

      expect(url).toBe('https://build-time-api.com/api/v1')
      
      import.meta.env = originalEnv
    })

    it('should use production fallback if no other URL available', () => {
      const url = getApiBaseUrl()

      expect(url).toBe('https://cacaoscan-backend.onrender.com/api/v1')
    })

    it('should correct relative runtime URL', () => {
      globalThis.__API_BASE_URL__ = '/api/v1'
      globalThis.location = { hostname: 'example.com' }

      const url = getApiBaseUrl()

      expect(url).toContain('https://')
      expect(url).toContain('example.com')
    })
  })

  describe('getApiBaseUrlWithoutPath', () => {
    it('should remove /api/v1 from URL', () => {
      const url = getApiBaseUrlWithoutPath()

      expect(url).not.toContain('/api/v1')
    })

    it('should handle URL with /api/v1', () => {
      globalThis.__API_BASE_URL__ = 'https://api.example.com/api/v1'
      globalThis.location = { hostname: 'example.com' }

      const url = getApiBaseUrlWithoutPath()

      expect(url).toBe('https://api.example.com')
    })
  })

  describe('getApiBaseUrlWithPath', () => {
    it('should ensure URL ends with /api/v1', () => {
      globalThis.__API_BASE_URL__ = 'https://api.example.com'
      globalThis.location = { hostname: 'example.com' }

      const url = getApiBaseUrlWithPath()

      expect(url).toContain('/api/v1')
      expect(url).not.toContain('/api/v1/')
    })

    it('should not duplicate /api/v1 if already present', () => {
      globalThis.__API_BASE_URL__ = 'https://api.example.com/api/v1'
      globalThis.location = { hostname: 'example.com' }

      const url = getApiBaseUrlWithPath()

      expect(url).toBe('https://api.example.com/api/v1')
      expect(url.split('/api/v1').length).toBe(2)
    })
  })

  describe('isDevelopment', () => {
    it('should return true in development mode', () => {
      const originalEnv = import.meta.env
      import.meta.env = {
        ...originalEnv,
        DEV: true,
        MODE: 'development'
      }

      const result = isDevelopment()

      expect(result).toBe(true)
      
      import.meta.env = originalEnv
    })

    it('should return true for localhost', () => {
      globalThis.location = { hostname: 'localhost' }

      const result = isDevelopment()

      expect(result).toBe(true)
    })
  })

  describe('isProduction', () => {
    it('should return true in production mode', () => {
      const originalEnv = import.meta.env
      import.meta.env = {
        ...originalEnv,
        PROD: true,
        MODE: 'production'
      }

      const result = isProduction()

      expect(result).toBe(true)
      
      import.meta.env = originalEnv
    })

    it('should return false for localhost', () => {
      globalThis.location = { hostname: 'localhost' }

      const result = isProduction()

      expect(result).toBe(false)
    })
  })

  describe('API_CONFIG', () => {
    it('should export API_CONFIG object', () => {
      expect(API_CONFIG).toBeDefined()
      expect(API_CONFIG).toHaveProperty('baseUrl')
      expect(API_CONFIG).toHaveProperty('baseUrlWithoutPath')
      expect(API_CONFIG).toHaveProperty('baseUrlWithPath')
      expect(API_CONFIG).toHaveProperty('isDev')
      expect(API_CONFIG).toHaveProperty('isProd')
    })
  })
})


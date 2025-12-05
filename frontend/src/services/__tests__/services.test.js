/**
 * Tests unitarios para servicios de CacaoScan Frontend.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock de axios antes de importar api
// Create the mock instance directly in the mock factory
vi.mock('axios', () => {
  const mockAxiosInstance = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn(),
    interceptors: {
      request: {
        use: vi.fn()
      },
      response: {
        use: vi.fn()
      }
    },
    defaults: {
      baseURL: 'https://test-api.example.com/api/v1',
      timeout: 15000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    }
  }
  
  return {
    default: {
      create: vi.fn(() => mockAxiosInstance)
    }
  }
})

vi.mock('@/router', () => ({
  default: {
    push: vi.fn()
  }
}))

vi.mock('@/utils/apiConfig', () => ({
  getApiBaseUrl: vi.fn(() => 'https://test-api.example.com/api/v1')
}))

// Import api after mocks
import api from '../api.js'

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('exporta api service', () => {
    expect(api).toBeDefined()
    expect(typeof api.get).toBe('function')
    expect(typeof api.post).toBe('function')
  })
})


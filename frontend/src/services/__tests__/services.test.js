/**
 * Tests unitarios para servicios de CacaoScan Frontend.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import api from '../api.js'

// Mock de axios
vi.mock('axios')
const mockedAxios = axios

// Importar servicios
import api from '../api.js'
import authApi from '../authApi.js'
import predictionApi from '../predictionApi.js'
import fincasApi from '../fincasApi.js'
import lotesApi from '../lotesApi.js'
import adminApi from '../adminApi.js'

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


import { describe, it, expect, beforeEach, vi } from 'vitest'
import api from '../api'
import {
  getLotes,
  getLoteById,
  createLote,
  updateLote,
  deleteLote,
  getLoteStats,
  validateLoteData,
  formatLoteData,
  getVariedadesCacao,
  getEstadosLote
} from '../lotesApi'

vi.mock('../api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

vi.mock('@/utils/apiResponse', () => ({
  normalizeResponse: (data) => data.results || data || []
}))

// Test helpers
const createMockResponse = (data) => ({ data })

const createMockError = (message) => new Error(message)

const testApiCall = async (apiFunction, apiMethod, expectedUrl, expectedParams, mockResponse, expectedResult) => {
  apiMethod.mockResolvedValue(mockResponse)
  const result = await apiFunction(expectedParams)
  expect(apiMethod).toHaveBeenCalledWith(expectedUrl, expectedParams || {})
  if (expectedResult === undefined) {
    expect(result).toBeDefined()
  } else {
    expect(result).toEqual(expectedResult)
  }
}

const testApiError = async (apiFunction, apiMethod, params, errorMessage) => {
  const error = createMockError(errorMessage)
  apiMethod.mockRejectedValue(error)
  await expect(apiFunction(params)).rejects.toThrow(errorMessage)
}

describe('lotesApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getLotes', () => {
    it('should fetch lotes successfully', async () => {
      const mockResponse = createMockResponse({
        results: [
          { id: 1, identificador: 'Lote A', variedad: 'Criollo' },
          { id: 2, identificador: 'Lote B', variedad: 'Forastero' }
        ],
        count: 2
      })
      await testApiCall(getLotes, api.get, '/lotes/', { page: 1 }, mockResponse)
    })

    it('should handle error when fetching lotes', async () => {
      await testApiError(getLotes, api.get, {}, 'Network error')
    })
  })

  describe('getLoteById', () => {
    it('should fetch lote by id successfully', async () => {
      const mockResponse = createMockResponse({ id: 1, identificador: 'Lote A', variedad: 'Criollo' })
      await testApiCall(getLoteById, api.get, '/lotes/1/', {}, mockResponse, mockResponse.data)
    })

    it('should handle error when fetching lote by id', async () => {
      await testApiError(getLoteById, api.get, 999, 'Not found')
    })
  })

  describe('createLote', () => {
    it('should create lote successfully', async () => {
      const loteData = {
        identificador: 'Lote Nuevo',
        variedad: 'Criollo',
        finca: { id: 1 },
        fecha_plantacion: '2024-01-01',
        area_hectareas: 5.5
      }
      const mockResponse = createMockResponse({ id: 3, ...loteData })
      api.post.mockResolvedValue(mockResponse)

      const result = await createLote(loteData)

      expect(api.post).toHaveBeenCalledWith('/lotes/', loteData, {})
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when creating lote', async () => {
      await testApiError(createLote, api.post, {}, 'Validation error')
    })
  })

  describe('updateLote', () => {
    it('should update lote successfully', async () => {
      const loteData = { identificador: 'Lote Actualizado' }
      const mockResponse = createMockResponse({ id: 1, ...loteData })
      api.put.mockResolvedValue(mockResponse)

      const result = await updateLote(1, loteData)

      expect(api.put).toHaveBeenCalledWith('/lotes/1/update/', loteData, {})
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when updating lote', async () => {
      await testApiError(updateLote, api.put, [1, {}], 'Update error')
    })
  })

  describe('deleteLote', () => {
    it('should delete lote successfully', async () => {
      api.delete.mockResolvedValue({})
      await deleteLote(1)
      expect(api.delete).toHaveBeenCalledWith('/lotes/1/delete/', {})
    })

    it('should handle error when deleting lote', async () => {
      await testApiError(deleteLote, api.delete, 1, 'Delete error')
    })
  })

  describe('getLoteStats', () => {
    it('should get lote stats successfully', async () => {
      const mockResponse = createMockResponse({ total_analisis: 10, calidad_promedio: 85 })
      await testApiCall(getLoteStats, api.get, '/lotes/1/stats/', {}, mockResponse, mockResponse.data)
    })

    it('should handle error when getting stats', async () => {
      await testApiError(getLoteStats, api.get, 1, 'Stats error')
    })
  })

  describe('validateLoteData', () => {
    it('should validate valid lote data', () => {
      const loteData = {
        finca: { id: 1 },
        identificador: 'Lote Test',
        variedad: 'Criollo',
        fecha_plantacion: '2024-01-01',
        area_hectareas: 5.5
      }

      const result = validateLoteData(loteData)

      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should reject lote data without finca', () => {
      const loteData = {
        identificador: 'Lote Test',
        variedad: 'Criollo'
      }

      const result = validateLoteData(loteData)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('La finca es requerida')
    })

    it('should reject lote data without identificador', () => {
      const loteData = {
        finca: { id: 1 },
        variedad: 'Criollo'
      }

      const result = validateLoteData(loteData)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('El identificador del lote es requerido')
    })

    it('should reject lote data with identificador too long', () => {
      const loteData = {
        finca: { id: 1 },
        identificador: 'A'.repeat(51),
        variedad: 'Criollo'
      }

      const result = validateLoteData(loteData)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('El identificador no puede exceder 50 caracteres')
    })

    it('should reject lote data with invalid area', () => {
      const loteData = {
        finca: { id: 1 },
        identificador: 'Lote Test',
        variedad: 'Criollo',
        area_hectareas: -5
      }

      const result = validateLoteData(loteData)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('El área en hectáreas debe ser un número positivo')
    })

    it('should reject lote data with invalid date range', () => {
      const loteData = {
        finca: { id: 1 },
        identificador: 'Lote Test',
        variedad: 'Criollo',
        fecha_plantacion: '2024-01-31',
        fecha_cosecha: '2024-01-01',
        area_hectareas: 5.5
      }

      const result = validateLoteData(loteData)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('La fecha de cosecha no puede ser anterior a la fecha de plantación')
    })
  })

  describe('formatLoteData', () => {
    it('should format lote data correctly', () => {
      const loteData = {
        identificador: '  Lote Test  ',
        variedad: '  Criollo  ',
        descripcion: '  Descripción  ',
        area_hectareas: '5.5',
        activa: false
      }

      const formatted = formatLoteData(loteData)

      expect(formatted.identificador).toBe('Lote Test')
      expect(formatted.variedad).toBe('Criollo')
      expect(formatted.descripcion).toBe('Descripción')
      expect(formatted.area_hectareas).toBe(5.5)
      expect(formatted.activa).toBe(false)
    })

    it('should set activa to true if not provided', () => {
      const loteData = {
        identificador: 'Lote Test',
        variedad: 'Criollo'
      }

      const formatted = formatLoteData(loteData)

      expect(formatted.activa).toBe(true)
    })
  })

  describe('getVariedadesCacao', () => {
    it('should return list of cacao varieties', () => {
      const variedades = getVariedadesCacao()

      expect(Array.isArray(variedades)).toBe(true)
      expect(variedades.length).toBeGreaterThan(0)
      expect(variedades).toContain('Criollo')
      expect(variedades).toContain('Forastero')
      expect(variedades).toContain('Trinitario')
    })
  })

  describe('getEstadosLote', () => {
    it('should return list of lote states', () => {
      const estados = getEstadosLote()

      expect(Array.isArray(estados)).toBe(true)
      expect(estados.length).toBeGreaterThan(0)
      expect(estados[0]).toHaveProperty('value')
      expect(estados[0]).toHaveProperty('label')
      expect(estados.find(e => e.value === 'activo')).toBeDefined()
    })
  })
})

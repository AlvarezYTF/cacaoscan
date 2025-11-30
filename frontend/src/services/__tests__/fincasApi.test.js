import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  getFincas,
  getFincaById,
  createFinca,
  updateFinca,
  deleteFinca,
  activateFinca,
  getFincaStats,
  getLotesByFinca,
  validateFincaData,
  formatFincaData,
  getDepartamentosColombia,
  getMunicipiosByDepartamento
} from '../fincasApi'
import api from '../api'

vi.mock('../api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

vi.mock('@/utils/apiResponse', () => ({
  normalizeResponse: (data) => data
}))

describe('fincasApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getFincas', () => {
    it('should fetch fincas successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, nombre: 'Finca 1' },
            { id: 2, nombre: 'Finca 2' }
          ],
          count: 2
        }
      }

      api.get.mockResolvedValue(mockResponse)

      const result = await getFincas({ page: 1 })

      expect(api.get).toHaveBeenCalledWith('/fincas/', { params: { page: 1 } })
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when fetching fincas', async () => {
      const error = new Error('Network error')
      api.get.mockRejectedValue(error)

      await expect(getFincas()).rejects.toThrow('Network error')
    })
  })

  describe('getFincaById', () => {
    it('should fetch finca by id successfully', async () => {
      const mockResponse = {
        data: { id: 1, nombre: 'Finca 1' }
      }

      api.get.mockResolvedValue(mockResponse)

      const result = await getFincaById(1)

      expect(api.get).toHaveBeenCalledWith('/fincas/1/')
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when fetching finca by id', async () => {
      const error = new Error('Not found')
      api.get.mockRejectedValue(error)

      await expect(getFincaById(1)).rejects.toThrow('Not found')
    })
  })

  describe('createFinca', () => {
    it('should create finca successfully', async () => {
      const fincaData = {
        nombre: 'Finca Nueva',
        municipio: 'Medellín',
        departamento: 'Antioquia',
        hectareas: 10.5
      }

      const mockResponse = {
        data: { id: 1, ...fincaData }
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await createFinca(fincaData)

      expect(api.post).toHaveBeenCalledWith('/fincas/', fincaData)
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when creating finca', async () => {
      const error = new Error('Validation error')
      api.post.mockRejectedValue(error)

      await expect(createFinca({})).rejects.toThrow('Validation error')
    })
  })

  describe('updateFinca', () => {
    it('should update finca successfully', async () => {
      const fincaData = {
        nombre: 'Finca Actualizada'
      }

      const mockResponse = {
        data: { id: 1, ...fincaData }
      }

      api.put.mockResolvedValue(mockResponse)

      const result = await updateFinca(1, fincaData)

      expect(api.put).toHaveBeenCalledWith('/fincas/1/update/', fincaData)
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when updating finca', async () => {
      const error = new Error('Update error')
      api.put.mockRejectedValue(error)

      await expect(updateFinca(1, {})).rejects.toThrow('Update error')
    })
  })

  describe('deleteFinca', () => {
    it('should delete finca successfully', async () => {
      api.delete.mockResolvedValue({})

      await deleteFinca(1)

      expect(api.delete).toHaveBeenCalledWith('/fincas/1/delete/')
    })

    it('should handle error when deleting finca', async () => {
      const error = new Error('Delete error')
      api.delete.mockRejectedValue(error)

      await expect(deleteFinca(1)).rejects.toThrow('Delete error')
    })
  })

  describe('activateFinca', () => {
    it('should activate finca successfully', async () => {
      const mockResponse = {
        data: { id: 1, activa: true }
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await activateFinca(1)

      expect(api.post).toHaveBeenCalledWith('/fincas/1/activate/')
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('getFincaStats', () => {
    it('should get finca stats successfully', async () => {
      const mockResponse = {
        data: { total_lotes: 5, total_analisis: 10 }
      }

      api.get.mockResolvedValue(mockResponse)

      const result = await getFincaStats(1)

      expect(api.get).toHaveBeenCalledWith('/fincas/1/stats/')
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('getLotesByFinca', () => {
    it('should get lotes by finca successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, nombre: 'Lote 1' }
          ]
        }
      }

      api.get.mockResolvedValue(mockResponse)

      const result = await getLotesByFinca(1, { page: 1 })

      expect(api.get).toHaveBeenCalledWith('/fincas/1/lotes/', { params: { page: 1 } })
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('validateFincaData', () => {
    it('should validate valid finca data', () => {
      const fincaData = {
        nombre: 'Finca Test',
        ubicacion: 'Ubicación test',
        municipio: 'Medellín',
        departamento: 'Antioquia',
        hectareas: 10.5
      }

      const result = validateFincaData(fincaData)

      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should reject finca data with missing required fields', () => {
      const fincaData = {
        nombre: '',
        hectareas: 10.5
      }

      const result = validateFincaData(fincaData)

      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
    })

    it('should reject finca data with invalid hectareas', () => {
      const fincaData = {
        nombre: 'Finca Test',
        ubicacion: 'Ubicación',
        municipio: 'Medellín',
        departamento: 'Antioquia',
        hectareas: -5
      }

      const result = validateFincaData(fincaData)

      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('hectáreas'))).toBe(true)
    })

    it('should reject finca data with invalid coordinates', () => {
      const fincaData = {
        nombre: 'Finca Test',
        ubicacion: 'Ubicación',
        municipio: 'Medellín',
        departamento: 'Antioquia',
        hectareas: 10.5,
        coordenadas_lat: 100,
        coordenadas_lng: -200
      }

      const result = validateFincaData(fincaData)

      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('latitud') || e.includes('longitud'))).toBe(true)
    })

    it('should reject finca data with description too long', () => {
      const fincaData = {
        nombre: 'Finca Test',
        ubicacion: 'Ubicación',
        municipio: 'Medellín',
        departamento: 'Antioquia',
        hectareas: 10.5,
        descripcion: 'a'.repeat(1001)
      }

      const result = validateFincaData(fincaData)

      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('descripción'))).toBe(true)
    })
  })

  describe('formatFincaData', () => {
    it('should format finca data correctly', () => {
      const fincaData = {
        nombre: '  Finca Test  ',
        ubicacion: '  Ubicación  ',
        municipio: 'Medellín',
        departamento: 'Antioquia',
        hectareas: '10.5',
        coordenadas_lat: '4.6097',
        coordenadas_lng: '-74.0817',
        descripcion: '  Descripción  '
      }

      const formatted = formatFincaData(fincaData)

      expect(formatted.nombre).toBe('Finca Test')
      expect(formatted.ubicacion).toBe('Ubicación')
      expect(formatted.hectareas).toBe(10.5)
      expect(formatted.coordenadas_lat).toBe(4.6097)
      expect(formatted.coordenadas_lng).toBe(-74.0817)
      expect(formatted.descripcion).toBe('Descripción')
      expect(formatted.activa).toBe(true)
    })

    it('should handle null coordinates', () => {
      const fincaData = {
        nombre: 'Finca Test',
        municipio: 'Medellín',
        departamento: 'Antioquia',
        hectareas: 10.5,
        coordenadas_lat: null,
        coordenadas_lng: ''
      }

      const formatted = formatFincaData(fincaData)

      expect(formatted.coordenadas_lat).toBe(null)
      expect(formatted.coordenadas_lng).toBe(null)
    })

    it('should remove invalid fields', () => {
      const fincaData = {
        nombre: 'Finca Test',
        municipio: 'Medellín',
        departamento: 'Antioquia',
        hectareas: 10.5,
        id: 999,
        created_at: '2024-01-01',
        total_lotes: 5
      }

      const formatted = formatFincaData(fincaData)

      expect(formatted.id).toBeUndefined()
      expect(formatted.created_at).toBeUndefined()
      expect(formatted.total_lotes).toBeUndefined()
    })
  })

  describe('getDepartamentosColombia', () => {
    it('should return list of departamentos', () => {
      const departamentos = getDepartamentosColombia()

      expect(Array.isArray(departamentos)).toBe(true)
      expect(departamentos.length).toBeGreaterThan(0)
      expect(departamentos).toContain('Antioquia')
      expect(departamentos).toContain('Cundinamarca')
    })
  })

  describe('getMunicipiosByDepartamento', () => {
    it('should return municipios for valid departamento', () => {
      const municipios = getMunicipiosByDepartamento('Antioquia')

      expect(Array.isArray(municipios)).toBe(true)
      expect(municipios.length).toBeGreaterThan(0)
      expect(municipios).toContain('Medellín')
    })

    it('should return empty array for invalid departamento', () => {
      const municipios = getMunicipiosByDepartamento('Invalid')

      expect(municipios).toEqual([])
    })
  })
})


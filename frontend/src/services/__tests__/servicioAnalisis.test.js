import { describe, it, expect, beforeEach, vi } from 'vitest'
import servicioAnalisis from '../servicioAnalisis'
import { createMockApi } from '@/test/mocks'

const mockApi = createMockApi()

vi.mock('../api', () => ({
  default: mockApi
}))

vi.mock('@/utils/apiResponse', () => ({
  normalizeResponse: (data) => data.results || data || []
}))

describe('servicioAnalisis', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAnalisis', () => {
    it('should fetch analisis successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, tipo_analisis: 'Calidad', calidad: 85 },
            { id: 2, tipo_analisis: 'Defectos', calidad: 90 }
          ],
          count: 2
        }
      }
      mockApi.get.mockResolvedValue(mockResponse)

      const result = await servicioAnalisis.getAnalisis({ page: 1 })

      expect(mockApi.get).toHaveBeenCalledWith('/analisis/', { params: { page: 1 } })
      expect(result).toBeDefined()
    })

    it('should handle error when fetching analisis', async () => {
      const error = new Error('Network error')
      mockApi.get.mockRejectedValue(error)

      await expect(servicioAnalisis.getAnalisis()).rejects.toThrow('Network error')
    })
  })

  describe('createAnalisis', () => {
    it('should create analisis successfully', async () => {
      const analisisData = {
        tipo_analisis: 'Calidad',
        calidad: 85,
        imagen: 'image.jpg'
      }
      const mockResponse = {
        data: { id: 1, ...analisisData }
      }
      mockApi.post.mockResolvedValue(mockResponse)

      const result = await servicioAnalisis.createAnalisis(analisisData)

      expect(mockApi.post).toHaveBeenCalledWith('/analisis/', analisisData)
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when creating analisis', async () => {
      const error = new Error('Validation error')
      mockApi.post.mockRejectedValue(error)

      await expect(servicioAnalisis.createAnalisis({})).rejects.toThrow('Validation error')
    })
  })

  describe('getAnalisisById', () => {
    it('should fetch analisis by id successfully', async () => {
      const mockResponse = {
        data: { id: 1, tipo_analisis: 'Calidad', calidad: 85 }
      }
      mockApi.get.mockResolvedValue(mockResponse)

      const result = await servicioAnalisis.getAnalisisById(1)

      expect(mockApi.get).toHaveBeenCalledWith('/analisis/1/')
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when fetching analisis by id', async () => {
      const error = new Error('Not found')
      mockApi.get.mockRejectedValue(error)

      await expect(servicioAnalisis.getAnalisisById(999)).rejects.toThrow('Not found')
    })
  })

  describe('updateAnalisis', () => {
    it('should update analisis successfully', async () => {
      const analisisData = { calidad: 90 }
      const mockResponse = {
        data: { id: 1, ...analisisData }
      }
      mockApi.put.mockResolvedValue(mockResponse)

      const result = await servicioAnalisis.updateAnalisis(1, analisisData)

      expect(mockApi.put).toHaveBeenCalledWith('/analisis/1/', analisisData)
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when updating analisis', async () => {
      const error = new Error('Update error')
      mockApi.put.mockRejectedValue(error)

      await expect(servicioAnalisis.updateAnalisis(1, {})).rejects.toThrow('Update error')
    })
  })

  describe('deleteAnalisis', () => {
    it('should delete analisis successfully', async () => {
      const mockResponse = {
        data: { success: true }
      }
      mockApi.delete.mockResolvedValue(mockResponse)

      const result = await servicioAnalisis.deleteAnalisis(1)

      expect(mockApi.delete).toHaveBeenCalledWith('/analisis/1/')
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when deleting analisis', async () => {
      const error = new Error('Delete error')
      mockApi.delete.mockRejectedValue(error)

      await expect(servicioAnalisis.deleteAnalisis(1)).rejects.toThrow('Delete error')
    })
  })

  describe('getAnalisisStats', () => {
    it('should get analisis stats successfully', async () => {
      const mockResponse = {
        data: {
          total_analisis: 100,
          calidad_promedio: 85,
          analisis_por_tipo: {}
        }
      }
      mockApi.get.mockResolvedValue(mockResponse)

      const result = await servicioAnalisis.getAnalisisStats()

      expect(mockApi.get).toHaveBeenCalledWith('/analisis/stats/')
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when getting stats', async () => {
      const error = new Error('Stats error')
      mockApi.get.mockRejectedValue(error)

      await expect(servicioAnalisis.getAnalisisStats()).rejects.toThrow('Stats error')
    })
  })
})


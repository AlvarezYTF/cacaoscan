import { describe, it, expect, beforeEach, vi } from 'vitest'

vi.mock('../api', () => ({
  default: {
    get: vi.fn()
  }
}))

vi.mock('@/utils/apiConfig', () => ({
  getApiBaseUrlWithPath: vi.fn(() => 'http://localhost:8000/api/v1')
}))

import api from '../api'
import catalogosApi from '../catalogosApi'

describe('catalogosApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getParametrosPorTema', () => {
    it('should get parameters by theme successfully', async () => {
      const mockResponse = {
        data: [
          { codigo: 'CC', nombre: 'Cédula de Ciudadanía' },
          { codigo: 'CE', nombre: 'Cédula de Extranjería' }
        ]
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await catalogosApi.getParametrosPorTema('TIPO_DOC')

      expect(api.get).toHaveBeenCalledWith('/parametros/', { params: { tema: 'TIPO_DOC' } })
      expect(result).toEqual(mockResponse.data)
    })

    it('should fallback to alternative endpoint on error', async () => {
      const error1 = { response: { status: 404 } }
      const mockResponse = {
        data: [{ codigo: 'CC', nombre: 'Cédula' }]
      }
      api.get
        .mockRejectedValueOnce(error1)
        .mockResolvedValueOnce(mockResponse)

      const result = await catalogosApi.getParametrosPorTema('TIPO_DOC')

      expect(api.get).toHaveBeenCalledTimes(2)
      expect(api.get).toHaveBeenNthCalledWith(2, '/parametros/tema/TIPO_DOC/', { params: {} })
      expect(result).toEqual(mockResponse.data)
    })

    it('should fallback to second alternative endpoint', async () => {
      const error1 = { response: { status: 404 } }
      const error2 = { response: { status: 404 } }
      const mockTemasResponse = {
        data: [
          { id: 1, codigo: 'TIPO_DOC', nombre: 'Tipo de Documento' }
        ]
      }
      const mockParametrosResponse = {
        data: [{ codigo: 'CC', nombre: 'Cédula' }]
      }
      api.get
        .mockRejectedValueOnce(error1)
        .mockRejectedValueOnce(error2)
        .mockResolvedValueOnce(mockTemasResponse)
        .mockResolvedValueOnce(mockParametrosResponse)

      const result = await catalogosApi.getParametrosPorTema('TIPO_DOC')

      expect(api.get).toHaveBeenCalledTimes(4)
      expect(api.get).toHaveBeenNthCalledWith(3, '/temas/', { params: {} })
      expect(api.get).toHaveBeenNthCalledWith(4, '/temas/1/parametros/', { params: {} })
      expect(result).toEqual(mockParametrosResponse.data)
    })

    it('should throw error if all endpoints fail', async () => {
      const error = { response: { status: 500 } }
      api.get
        .mockRejectedValueOnce(error)
        .mockRejectedValueOnce(error)
        .mockRejectedValueOnce(error) // falla también la llamada a /temas/

      await expect(catalogosApi.getParametrosPorTema('TIPO_DOC')).rejects.toEqual(error)
    })
  })

  describe('getTemas', () => {
    it('should get themes successfully', async () => {
      const mockResponse = {
        data: [
          { codigo: 'TIPO_DOC', nombre: 'Tipo de Documento' },
          { codigo: 'SEXO', nombre: 'Sexo' }
        ]
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await catalogosApi.getTemas()

      expect(api.get).toHaveBeenCalledWith('/temas/', { params: {} })
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when getting themes', async () => {
      const error = new Error('Network error')
      api.get.mockRejectedValue(error)

      await expect(catalogosApi.getTemas()).rejects.toThrow('Network error')
    })
  })

  describe('getDepartamentos', () => {
    it('should get departamentos successfully', async () => {
      const mockResponse = {
        data: [
          { codigo: '05', nombre: 'Antioquia' },
          { codigo: '11', nombre: 'Bogotá' }
        ]
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await catalogosApi.getDepartamentos()

      expect(api.get).toHaveBeenCalledWith('/departamentos/', { params: {} })
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when getting departamentos', async () => {
      const error = new Error('Network error')
      api.get.mockRejectedValue(error)

      await expect(catalogosApi.getDepartamentos()).rejects.toThrow('Network error')
    })
  })

  describe('getMunicipiosPorDepartamento', () => {
    it('should get municipios by departamento successfully', async () => {
      const mockResponse = {
        data: [
          { codigo: '05001', nombre: 'Medellín' },
          { codigo: '05002', nombre: 'Bello' }
        ]
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await catalogosApi.getMunicipiosPorDepartamento('05')

      expect(api.get).toHaveBeenCalledWith('/municipios/', { params: { departamento: '05' } })
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when getting municipios', async () => {
      const error = new Error('Network error')
      api.get.mockRejectedValue(error)

      await expect(catalogosApi.getMunicipiosPorDepartamento('05')).rejects.toThrow('Network error')
    })
  })

  describe('getDepartamentoPorCodigo', () => {
    beforeEach(() => {
      global.fetch = vi.fn()
    })

    it('should get departamento by code successfully', async () => {
      const mockDepartamentos = [
        { codigo: '05', nombre: 'Antioquia' },
        { codigo: '11', nombre: 'Bogotá' }
      ]
      
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ data: mockDepartamentos })
      })

      const result = await catalogosApi.getDepartamentoPorCodigo('05')

      expect(global.fetch).toHaveBeenCalled()
      expect(result).toEqual({ codigo: '05', nombre: 'Antioquia' })
    })

    it('should return undefined if departamento not found', async () => {
      const mockDepartamentos = [
        { codigo: '05', nombre: 'Antioquia' }
      ]
      
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ data: mockDepartamentos })
      })

      const result = await catalogosApi.getDepartamentoPorCodigo('99')

      expect(result).toBeUndefined()
    })

    it('should handle error when getting departamento by code', async () => {
      global.fetch.mockResolvedValue({
        ok: false,
        status: 500
      })

      await expect(catalogosApi.getDepartamentoPorCodigo('05')).rejects.toThrow()
    })
  })

  describe('getMunicipiosByDepartamento', () => {
    it('should get municipios by departamento id successfully', async () => {
      const mockResponse = {
        data: [
          { id: 1, nombre: 'Medellín' },
          { id: 2, nombre: 'Bello' }
        ]
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await catalogosApi.getMunicipiosByDepartamento(1)

      expect(api.get).toHaveBeenCalledWith('/municipios/', { params: { departamento: 1 } })
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when getting municipios by departamento id', async () => {
      const error = new Error('HTTP 500')
      error.response = {
        status: 500,
        data: { detail: 'HTTP 500' }
      }
      api.get.mockRejectedValue(error)

      await expect(catalogosApi.getMunicipiosByDepartamento(1)).rejects.toThrow('HTTP 500')
    })
  })

  describe('getParametrosByTema', () => {
    it('should be an alias for getParametrosPorTema', async () => {
      const mockResponse = {
        data: [{ codigo: 'CC', nombre: 'Cédula' }]
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await catalogosApi.getParametrosByTema('TIPO_DOC')

      expect(api.get).toHaveBeenCalledWith('/parametros/', { params: { tema: 'TIPO_DOC' } })
      expect(result).toEqual(mockResponse.data)
    })
  })
})


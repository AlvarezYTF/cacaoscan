/**
 * Unit tests for useCatalogos composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useCatalogos } from '../useCatalogos.js'
import { catalogosApi } from '@/services'

// Mock catalogosApi
vi.mock('@/services', () => ({
  catalogosApi: {
    getParametrosPorTema: vi.fn(),
    getDepartamentos: vi.fn(),
    getMunicipiosByDepartamento: vi.fn()
  }
}))

describe('useCatalogos', () => {
  let catalogos

  beforeEach(() => {
    vi.clearAllMocks()
    catalogos = useCatalogos()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(catalogos.tiposDocumento.value).toEqual([])
      expect(catalogos.generos.value).toEqual([])
      expect(catalogos.departamentos.value).toEqual([])
      expect(catalogos.municipios.value).toEqual([])
      expect(catalogos.isLoadingCatalogos.value).toBe(false)
    })
  })

  describe('cargarCatalogos', () => {
    it('should load catalogos successfully', async () => {
      catalogosApi.getParametrosPorTema.mockResolvedValueOnce([{ id: 1, nombre: 'CC' }])
      catalogosApi.getParametrosPorTema.mockResolvedValueOnce([{ id: 1, nombre: 'M' }])
      catalogosApi.getDepartamentos.mockResolvedValue([{ id: 1, nombre: 'Antioquia' }])

      await catalogos.cargarCatalogos()

      expect(catalogosApi.getParametrosPorTema).toHaveBeenCalledWith('TIPO_DOC')
      expect(catalogosApi.getParametrosPorTema).toHaveBeenCalledWith('SEXO')
      expect(catalogosApi.getDepartamentos).toHaveBeenCalled()
      expect(catalogos.isLoadingCatalogos.value).toBe(false)
    })

    it('should handle error gracefully', async () => {
      catalogosApi.getParametrosPorTema.mockRejectedValue(new Error('Network error'))

      await catalogos.cargarCatalogos()

      expect(catalogos.error.value).toBeTruthy()
      expect(catalogos.isLoadingCatalogos.value).toBe(false)
    })
  })

  describe('cargarMunicipios', () => {
    it('should load municipios by departamento ID', async () => {
      const mockMunicipios = [{ id: 1, nombre: 'Medellín' }]
      catalogosApi.getMunicipiosByDepartamento.mockResolvedValue(mockMunicipios)

      await catalogos.cargarMunicipios(1)

      expect(catalogosApi.getMunicipiosByDepartamento).toHaveBeenCalledWith(1)
      expect(catalogos.municipios.value).toEqual(mockMunicipios)
    })

    it('should clear municipios when no departamentoId', async () => {
      await catalogos.cargarMunicipios(null)

      expect(catalogos.municipios.value).toEqual([])
    })
  })

  describe('limpiarMunicipios', () => {
    it('should clear municipios', () => {
      catalogos.municipios.value = [{ id: 1, nombre: 'Medellín' }]
      
      catalogos.limpiarMunicipios()
      
      expect(catalogos.municipios.value).toEqual([])
    })
  })
})


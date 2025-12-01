import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useCatalogos } from '../useCatalogos'
import { catalogosApi } from '@/services'

vi.mock('@/services', () => ({
  catalogosApi: {
    getParametrosPorTema: vi.fn(),
    getDepartamentos: vi.fn(),
    getMunicipiosByDepartamento: vi.fn()
  }
}))

vi.mock('vue', async () => {
  const actual = await vi.importActual('vue')
  return {
    ...actual,
    onMounted: vi.fn((fn) => fn())
  }
})

describe('useCatalogos', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    catalogosApi.getParametrosPorTema.mockResolvedValue([])
    catalogosApi.getDepartamentos.mockResolvedValue([])
    catalogosApi.getMunicipiosByDepartamento.mockResolvedValue([])
  })

  it('should initialize with empty arrays', () => {
    const { tiposDocumento, generos, departamentos, municipios, isLoadingCatalogos, error } = useCatalogos()

    expect(tiposDocumento.value).toEqual([])
    expect(generos.value).toEqual([])
    expect(departamentos.value).toEqual([])
    expect(municipios.value).toEqual([])
    expect(isLoadingCatalogos.value).toBe(false)
    expect(error.value).toBe(null)
  })

  it('should load catalogos successfully', async () => {
    const mockTiposDoc = [{ codigo: 'CC', nombre: 'Cédula' }]
    const mockGeneros = [{ codigo: 'M', nombre: 'Masculino' }]
    const mockDepartamentos = [{ id: 1, codigo: '05', nombre: 'Antioquia' }]

    catalogosApi.getParametrosPorTema
      .mockResolvedValueOnce(mockTiposDoc)
      .mockResolvedValueOnce(mockGeneros)
    catalogosApi.getDepartamentos.mockResolvedValue(mockDepartamentos)

    const { cargarCatalogos, tiposDocumento, generos, departamentos, isLoadingCatalogos } = useCatalogos()

    await cargarCatalogos()

    expect(catalogosApi.getParametrosPorTema).toHaveBeenCalledWith('TIPO_DOC')
    expect(catalogosApi.getParametrosPorTema).toHaveBeenCalledWith('SEXO')
    expect(catalogosApi.getDepartamentos).toHaveBeenCalled()
    expect(tiposDocumento.value).toEqual(mockTiposDoc)
    expect(generos.value).toEqual(mockGeneros)
    expect(departamentos.value).toEqual(mockDepartamentos)
    expect(isLoadingCatalogos.value).toBe(false)
  })

  it('should handle error when loading catalogos', async () => {
    const error = new Error('Network error')
    catalogosApi.getParametrosPorTema.mockRejectedValue(error)
    catalogosApi.getDepartamentos.mockRejectedValue(error)

    const { cargarCatalogos, error: errorRef, tiposDocumento, generos, departamentos } = useCatalogos()

    await cargarCatalogos()

    expect(errorRef.value).toBe('Error al cargar catálogos')
    expect(tiposDocumento.value).toEqual([])
    expect(generos.value).toEqual([])
    expect(departamentos.value).toEqual([])
  })

  it('should load municipios by departamento id (number)', async () => {
    const mockMunicipios = [
      { id: 1, nombre: 'Medellín' },
      { id: 2, nombre: 'Bello' }
    ]
    catalogosApi.getMunicipiosByDepartamento.mockResolvedValue(mockMunicipios)

    const { cargarMunicipios, municipios } = useCatalogos()

    await cargarMunicipios(1)

    expect(catalogosApi.getMunicipiosByDepartamento).toHaveBeenCalledWith(1)
    expect(municipios.value).toEqual(mockMunicipios)
  })

  it('should load municipios by departamento code (string)', async () => {
    const mockDepartamentos = [
      { id: 1, codigo: '05', nombre: 'Antioquia' }
    ]
    const mockMunicipios = [
      { id: 1, nombre: 'Medellín' }
    ]

    catalogosApi.getDepartamentos.mockResolvedValue(mockDepartamentos)
    catalogosApi.getMunicipiosByDepartamento.mockResolvedValue(mockMunicipios)

    const { cargarCatalogos, cargarMunicipios, municipios } = useCatalogos()
    await cargarCatalogos()

    await cargarMunicipios('05')

    expect(catalogosApi.getMunicipiosByDepartamento).toHaveBeenCalledWith(1)
    expect(municipios.value).toEqual(mockMunicipios)
  })

  it('should clear municipios when departamentoId is empty', async () => {
    const { cargarMunicipios, municipios } = useCatalogos()
    municipios.value = [{ id: 1, nombre: 'Medellín' }]

    await cargarMunicipios(null)

    expect(municipios.value).toEqual([])
    expect(catalogosApi.getMunicipiosByDepartamento).not.toHaveBeenCalled()
  })

  it('should clear municipios', () => {
    const { limpiarMunicipios, municipios } = useCatalogos()
    municipios.value = [{ id: 1, nombre: 'Medellín' }]

    limpiarMunicipios()

    expect(municipios.value).toEqual([])
  })

  it('should handle error when loading municipios', async () => {
    const error = new Error('Network error')
    catalogosApi.getMunicipiosByDepartamento.mockRejectedValue(error)

    const { cargarMunicipios, municipios } = useCatalogos()

    await cargarMunicipios(1)

    expect(municipios.value).toEqual([])
  })
})


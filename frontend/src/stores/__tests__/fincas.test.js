import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useFincasStore } from '../fincas.js'

// Mock fincasApi
const mockFincasApi = {
  getFincas: vi.fn(),
  getFincaById: vi.fn(),
  createFinca: vi.fn(),
  updateFinca: vi.fn(),
  deleteFinca: vi.fn(),
  activateFinca: vi.fn()
}

vi.mock('@/services/fincasApi', () => ({
  getFincas: (...args) => mockFincasApi.getFincas(...args),
  getFincaById: (...args) => mockFincasApi.getFincaById(...args),
  createFinca: (...args) => mockFincasApi.createFinca(...args),
  updateFinca: (...args) => mockFincasApi.updateFinca(...args),
  deleteFinca: (...args) => mockFincasApi.deleteFinca(...args),
  activateFinca: (...args) => mockFincasApi.activateFinca(...args)
}))

describe('FincasStore', () => {
  let fincasStore

  beforeEach(() => {
    setActivePinia(createPinia())
    fincasStore = useFincasStore()
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      expect(fincasStore.fincas).toEqual([])
      expect(fincasStore.selected).toBe(null)
      expect(fincasStore.loading).toBe(false)
      expect(fincasStore.error).toBe(null)
    })
  })

  describe('fetchFincas', () => {
    it('should fetch fincas successfully', async () => {
      const mockFincas = [
        { id: 1, nombre: 'Finca 1', activa: true },
        { id: 2, nombre: 'Finca 2', activa: true }
      ]

      mockFincasApi.getFincas.mockResolvedValue(mockFincas)

      await fincasStore.fetchFincas()

      expect(mockFincasApi.getFincas).toHaveBeenCalledWith({})
      expect(fincasStore.fincas).toEqual(mockFincas)
      expect(fincasStore.loading).toBe(false)
      expect(fincasStore.error).toBe(null)
    })

    it('should handle array response', async () => {
      const mockFincas = [{ id: 1, nombre: 'Finca 1' }]

      mockFincasApi.getFincas.mockResolvedValue(mockFincas)

      await fincasStore.fetchFincas()

      expect(fincasStore.fincas).toEqual(mockFincas)
    })

    it('should handle paginated response with results', async () => {
      const mockResponse = {
        results: [
          { id: 1, nombre: 'Finca 1' },
          { id: 2, nombre: 'Finca 2' }
        ],
        count: 2,
        page: 1
      }

      mockFincasApi.getFincas.mockResolvedValue(mockResponse)

      await fincasStore.fetchFincas()

      expect(fincasStore.fincas).toEqual(mockResponse.results)
    })

    it('should handle fetch with params', async () => {
      const params = { activa: true, page: 1 }

      mockFincasApi.getFincas.mockResolvedValue([])

      await fincasStore.fetchFincas(params)

      expect(mockFincasApi.getFincas).toHaveBeenCalledWith(params)
    })

    it('should handle fetch errors', async () => {
      const error = {
        response: {
          data: {
            detail: 'Error fetching fincas'
          }
        },
        message: 'Network error'
      }

      mockFincasApi.getFincas.mockRejectedValue(error)

      await fincasStore.fetchFincas()

      expect(fincasStore.error).toBe('Error fetching fincas')
      expect(fincasStore.loading).toBe(false)
    })

    it('should set loading state during fetch', async () => {
      const delayedPromise = new Promise((resolve) => setTimeout(resolve, 100))
      mockFincasApi.getFincas.mockImplementation(() => delayedPromise)

      const fetchPromise = fincasStore.fetchFincas()

      expect(fincasStore.loading).toBe(true)

      await fetchPromise

      expect(fincasStore.loading).toBe(false)
    })
  })

  describe('fetchById', () => {
    it('should fetch finca by id successfully', async () => {
      const fincaId = 1
      const mockFinca = {
        id: 1,
        nombre: 'Finca 1',
        activa: true
      }

      mockFincasApi.getFincaById.mockResolvedValue(mockFinca)

      const result = await fincasStore.fetchById(fincaId)

      expect(mockFincasApi.getFincaById).toHaveBeenCalledWith(fincaId)
      expect(result).toEqual(mockFinca)
      expect(fincasStore.selected).toEqual(mockFinca)
      expect(fincasStore.loading).toBe(false)
      expect(fincasStore.error).toBe(null)
    })

    it('should handle fetchById errors', async () => {
      const fincaId = 999
      const error = {
        response: {
          data: {
            detail: 'Finca not found'
          }
        }
      }

      mockFincasApi.getFincaById.mockRejectedValue(error)

      await expect(fincasStore.fetchById(fincaId)).rejects.toEqual(error)

      expect(fincasStore.error).toBe('Finca not found')
      expect(fincasStore.loading).toBe(false)
    })
  })

  describe('create', () => {
    it('should create finca successfully', async () => {
      const fincaData = {
        nombre: 'New Finca',
        ubicacion: 'Test Location'
      }

      const existingFincas = [
        { id: 1, nombre: 'Existing Finca' }
      ]

      fincasStore.fincas = existingFincas
      mockFincasApi.createFinca.mockResolvedValue({ id: 2, ...fincaData })
      mockFincasApi.getFincas.mockResolvedValue([...existingFincas, { id: 2, ...fincaData }])

      const result = await fincasStore.create(fincaData)

      expect(mockFincasApi.createFinca).toHaveBeenCalledWith(fincaData)
      expect(mockFincasApi.getFincas).toHaveBeenCalled()
      expect(result).toBe(true)
      expect(fincasStore.loading).toBe(false)
    })

    it('should handle create errors', async () => {
      const fincaData = { nombre: 'New Finca' }
      const error = {
        response: {
          data: {
            detail: 'Validation error'
          }
        }
      }

      mockFincasApi.createFinca.mockRejectedValue(error)

      await expect(fincasStore.create(fincaData)).rejects.toEqual(error)

      expect(fincasStore.error).toBe('Validation error')
      expect(fincasStore.loading).toBe(false)
    })
  })

  describe('update', () => {
    it('should update finca successfully', async () => {
      const fincaId = 1
      const fincaData = {
        nombre: 'Updated Finca'
      }

      const existingFincas = [
        { id: 1, nombre: 'Old Name' }
      ]

      fincasStore.fincas = existingFincas
      mockFincasApi.updateFinca.mockResolvedValue({ id: 1, ...fincaData })
      mockFincasApi.getFincas.mockResolvedValue([{ id: 1, ...fincaData }])

      const result = await fincasStore.update(fincaId, fincaData)

      expect(mockFincasApi.updateFinca).toHaveBeenCalledWith(fincaId, fincaData)
      expect(mockFincasApi.getFincas).toHaveBeenCalled()
      expect(result).toBe(true)
      expect(fincasStore.loading).toBe(false)
    })

    it('should handle update errors', async () => {
      const fincaId = 1
      const fincaData = { nombre: 'Updated' }
      const error = {
        response: {
          data: {
            detail: 'Update failed'
          }
        }
      }

      mockFincasApi.updateFinca.mockRejectedValue(error)

      await expect(fincasStore.update(fincaId, fincaData)).rejects.toEqual(error)

      expect(fincasStore.error).toBe('Update failed')
    })
  })

  describe('remove', () => {
    it('should remove finca successfully', async () => {
      const fincaId = 1
      const existingFincas = [
        { id: 1, nombre: 'Finca 1' },
        { id: 2, nombre: 'Finca 2' }
      ]

      fincasStore.fincas = existingFincas
      fincasStore.selected = { id: 1, nombre: 'Finca 1' }

      mockFincasApi.deleteFinca.mockResolvedValue({})
      mockFincasApi.getFincas.mockResolvedValue([{ id: 2, nombre: 'Finca 2' }])

      const result = await fincasStore.remove(fincaId)

      expect(mockFincasApi.deleteFinca).toHaveBeenCalledWith(fincaId)
      expect(mockFincasApi.getFincas).toHaveBeenCalled()
      expect(result).toBe(true)
      expect(fincasStore.selected).toBe(null)
      expect(fincasStore.loading).toBe(false)
    })

    it('should not clear selected if different finca', async () => {
      const fincaId = 1
      const selectedFinca = { id: 2, nombre: 'Finca 2' }

      fincasStore.selected = selectedFinca
      mockFincasApi.deleteFinca.mockResolvedValue({})
      mockFincasApi.getFincas.mockResolvedValue([])

      await fincasStore.remove(fincaId)

      expect(fincasStore.selected).toEqual(selectedFinca)
    })

    it('should handle remove errors', async () => {
      const fincaId = 1
      const error = {
        response: {
          data: {
            detail: 'Cannot delete'
          }
        }
      }

      mockFincasApi.deleteFinca.mockRejectedValue(error)

      await expect(fincasStore.remove(fincaId)).rejects.toEqual(error)

      expect(fincasStore.error).toBe('Cannot delete')
    })
  })

  describe('activate', () => {
    it('should activate finca successfully', async () => {
      const fincaId = 1

      mockFincasApi.activateFinca.mockResolvedValue({ id: 1, activa: true })
      mockFincasApi.getFincas.mockResolvedValue([{ id: 1, activa: true }])

      const result = await fincasStore.activate(fincaId)

      expect(mockFincasApi.activateFinca).toHaveBeenCalledWith(fincaId)
      expect(mockFincasApi.getFincas).toHaveBeenCalled()
      expect(result).toBe(true)
      expect(fincasStore.loading).toBe(false)
    })

    it('should handle activate errors', async () => {
      const fincaId = 1
      const error = {
        response: {
          data: {
            detail: 'Cannot activate'
          }
        }
      }

      mockFincasApi.activateFinca.mockRejectedValue(error)

      await expect(fincasStore.activate(fincaId)).rejects.toEqual(error)

      expect(fincasStore.error).toBe('Cannot activate')
    })
  })

  describe('clearError', () => {
    it('should clear error', () => {
      fincasStore.error = 'Some error'

      fincasStore.clearError()

      expect(fincasStore.error).toBe(null)
    })
  })

  describe('setSelected', () => {
    it('should set selected finca', () => {
      const finca = { id: 1, nombre: 'Selected Finca' }

      fincasStore.setSelected(finca)

      expect(fincasStore.selected).toEqual(finca)
    })
  })

  describe('clearSelected', () => {
    it('should clear selected finca', () => {
      fincasStore.selected = { id: 1, nombre: 'Finca' }

      fincasStore.clearSelected()

      expect(fincasStore.selected).toBe(null)
    })
  })
})


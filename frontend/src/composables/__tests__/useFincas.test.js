/**
 * Unit tests for useFincas composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useFincas } from '../useFincas.js'
import { getFincas, getFincaById, createFinca, updateFinca, deleteFinca } from '@/services/fincasApi'

// Mock dependencies
vi.mock('@/services/fincasApi', () => ({
  getFincas: vi.fn(),
  getFincaById: vi.fn(),
  createFinca: vi.fn(),
  updateFinca: vi.fn(),
  deleteFinca: vi.fn()
}))

vi.mock('@/services/apiErrorHandler', () => ({
  handleApiError: vi.fn((error) => ({
    message: error.message || 'Error'
  }))
}))

describe('useFincas', () => {
  let fincas

  beforeEach(() => {
    vi.clearAllMocks()
    fincas = useFincas()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(fincas.fincas.value).toEqual([])
      expect(fincas.currentFinca.value).toBe(null)
      expect(fincas.isLoading.value).toBe(false)
      expect(fincas.error.value).toBe(null)
      expect(fincas.hasFincas.value).toBe(false)
    })
  })

  describe('loadFincas', () => {
    it('should load fincas successfully', async () => {
      const mockResponse = {
        results: [{ id: 1, name: 'Finca 1' }],
        count: 1
      }
      getFincas.mockResolvedValue(mockResponse)

      await fincas.loadFincas()

      expect(getFincas).toHaveBeenCalled()
      expect(fincas.fincas.value).toEqual([{ id: 1, name: 'Finca 1' }])
      expect(fincas.isLoading.value).toBe(false)
    })

    it('should handle load error', async () => {
      const error = new Error('Network error')
      getFincas.mockRejectedValue(error)

      await expect(fincas.loadFincas()).rejects.toThrow()

      expect(fincas.error.value).toBeTruthy()
      expect(fincas.isLoading.value).toBe(false)
    })

    it('should append results for pagination', async () => {
      const page1Response = {
        results: [{ id: 1, name: 'Finca 1' }],
        count: 2
      }
      const page2Response = {
        results: [{ id: 2, name: 'Finca 2' }],
        count: 2
      }

      getFincas.mockResolvedValueOnce(page1Response)
      await fincas.loadFincas({}, 1, 20)

      getFincas.mockResolvedValueOnce(page2Response)
      await fincas.loadFincas({}, 2, 20)

      expect(fincas.fincas.value).toHaveLength(2)
    })
  })

  describe('loadFinca', () => {
    it('should load single finca', async () => {
      const mockFinca = { id: 1, name: 'Finca 1' }
      getFincaById.mockResolvedValue(mockFinca)

      const result = await fincas.loadFinca(1)

      expect(getFincaById).toHaveBeenCalledWith(1)
      expect(fincas.currentFinca.value).toEqual(mockFinca)
      expect(result).toEqual(mockFinca)
    })
  })

  describe('createFinca', () => {
    it('should create finca successfully', async () => {
      const fincaData = { name: 'New Finca' }
      const mockFinca = { id: 1, ...fincaData }
      createFinca.mockResolvedValue(mockFinca)
      const onFincaCreate = vi.fn()

      const fincasWithCallback = useFincas({ onFincaCreate })
      await fincasWithCallback.createFinca(fincaData)

      expect(createFinca).toHaveBeenCalledWith(fincaData)
      expect(onFincaCreate).toHaveBeenCalled()
    })
  })

  describe('updateFinca', () => {
    it('should update finca successfully', async () => {
      const fincaData = { id: 1, name: 'Updated Finca' }
      updateFinca.mockResolvedValue(fincaData)
      const onFincaUpdate = vi.fn()

      const fincasWithCallback = useFincas({ onFincaUpdate })
      await fincasWithCallback.updateFinca(1, fincaData)

      expect(updateFinca).toHaveBeenCalledWith(1, fincaData)
      expect(onFincaUpdate).toHaveBeenCalled()
    })
  })

  describe('deleteFinca', () => {
    it('should delete finca successfully', async () => {
      deleteFinca.mockResolvedValue()
      const onFincaDelete = vi.fn()

      const fincasWithCallback = useFincas({ onFincaDelete })
      await fincasWithCallback.deleteFinca(1)

      expect(deleteFinca).toHaveBeenCalledWith(1)
      expect(onFincaDelete).toHaveBeenCalled()
    })
  })

  describe('computed properties', () => {
    it('should compute hasFincas correctly', () => {
      fincas.fincas.value = [{ id: 1 }]
      expect(fincas.hasFincas.value).toBe(true)

      fincas.fincas.value = []
      expect(fincas.hasFincas.value).toBe(false)
    })

    it('should compute hasCurrentFinca correctly', () => {
      fincas.currentFinca.value = { id: 1 }
      expect(fincas.hasCurrentFinca.value).toBe(true)

      fincas.currentFinca.value = null
      expect(fincas.hasCurrentFinca.value).toBe(false)
    })

    it('should compute hasError correctly', () => {
      fincas.error.value = 'Error message'
      expect(fincas.hasError.value).toBe(true)

      fincas.error.value = null
      expect(fincas.hasError.value).toBe(false)
    })
  })

  describe('filters', () => {
    it('should set filters', () => {
      fincas.setFilters({ search: 'test' })
      expect(fincas.filters.value).toEqual({ search: 'test' })
    })

    it('should merge filters', () => {
      fincas.setFilters({ search: 'test' })
      fincas.setFilters({ departamento: 'Cundinamarca' })
      expect(fincas.filters.value).toEqual({
        search: 'test',
        departamento: 'Cundinamarca'
      })
    })

    it('should clear filters', () => {
      fincas.setFilters({ search: 'test', departamento: 'Cundinamarca' })
      fincas.clearFilters()
      expect(fincas.filters.value).toEqual({})
    })
  })

  describe('current finca management', () => {
    it('should set current finca', () => {
      const mockFinca = { id: 1, name: 'Finca 1' }
      fincas.setCurrentFinca(mockFinca)
      expect(fincas.currentFinca.value).toEqual(mockFinca)
    })

    it('should clear current finca', () => {
      fincas.setCurrentFinca({ id: 1, name: 'Finca 1' })
      fincas.clearCurrentFinca()
      expect(fincas.currentFinca.value).toBe(null)
    })
  })

  describe('pagination', () => {
    it('should handle pagination correctly', async () => {
      const mockResponse = {
        results: [{ id: 1, name: 'Finca 1' }],
        count: 25,
        next: 'http://api.example.com/fincas/?page=2',
        previous: null
      }
      getFincas.mockResolvedValue(mockResponse)

      await fincas.loadFincas({}, 1, 20)

      expect(fincas.pagination.value.totalItems).toBe(25)
      expect(fincas.pagination.value.currentPage).toBe(1)
    })

    it('should reset pagination on new search', async () => {
      const page1Response = {
        results: [{ id: 1, name: 'Finca 1' }],
        count: 2
      }
      const page2Response = {
        results: [{ id: 2, name: 'Finca 2' }],
        count: 2
      }

      getFincas.mockResolvedValueOnce(page1Response)
      await fincas.loadFincas({}, 1, 20)
      expect(fincas.pagination.value.currentPage).toBe(1)

      getFincas.mockResolvedValueOnce(page2Response)
      await fincas.loadFincas({ search: 'new' }, 1, 20)
      expect(fincas.pagination.value.currentPage).toBe(1)
    })
  })

  describe('create finca with callbacks', () => {
    it('should call onFincaCreate callback', async () => {
      const onFincaCreate = vi.fn()
      const fincasWithCallback = useFincas({ onFincaCreate })
      const fincaData = { name: 'New Finca' }
      const mockFinca = { id: 1, ...fincaData }
      createFinca.mockResolvedValue(mockFinca)

      await fincasWithCallback.create(fincaData)

      expect(onFincaCreate).toHaveBeenCalledWith(mockFinca)
    })

    it('should handle create error', async () => {
      const error = new Error('Create failed')
      createFinca.mockRejectedValue(error)

      await expect(fincas.create({ name: 'Test' })).rejects.toThrow()
      expect(fincas.error.value).toBeTruthy()
      expect(fincas.isLoading.value).toBe(false)
    })

    it('should update pagination totalItems on create', async () => {
      const fincaData = { name: 'New Finca' }
      const mockFinca = { id: 1, ...fincaData }
      createFinca.mockResolvedValue(mockFinca)
      fincas.pagination.value.totalItems = 5

      await fincas.create(fincaData)

      expect(fincas.pagination.value.totalItems).toBe(6)
    })
  })

  describe('update finca', () => {
    it('should update finca in list', async () => {
      fincas.fincas.value = [{ id: 1, name: 'Old Name' }]
      const updatedFinca = { id: 1, name: 'New Name' }
      updateFinca.mockResolvedValue(updatedFinca)

      await fincas.update(1, { name: 'New Name' })

      expect(fincas.fincas.value[0]).toEqual(updatedFinca)
    })

    it('should update current finca if it matches', async () => {
      fincas.currentFinca.value = { id: 1, name: 'Old Name' }
      const updatedFinca = { id: 1, name: 'New Name' }
      updateFinca.mockResolvedValue(updatedFinca)

      await fincas.update(1, { name: 'New Name' })

      expect(fincas.currentFinca.value).toEqual(updatedFinca)
    })

    it('should call onFincaUpdate callback', async () => {
      const onFincaUpdate = vi.fn()
      const fincasWithCallback = useFincas({ onFincaUpdate })
      const updatedFinca = { id: 1, name: 'Updated Name' }
      updateFinca.mockResolvedValue(updatedFinca)

      await fincasWithCallback.update(1, { name: 'Updated Name' })

      expect(onFincaUpdate).toHaveBeenCalledWith(updatedFinca)
    })

    it('should handle update error', async () => {
      const error = new Error('Update failed')
      updateFinca.mockRejectedValue(error)

      await expect(fincas.update(1, { name: 'Test' })).rejects.toThrow()
      expect(fincas.error.value).toBeTruthy()
    })
  })

  describe('delete finca', () => {
    beforeEach(() => {
      fincas.fincas.value = [
        { id: 1, name: 'Finca 1' },
        { id: 2, name: 'Finca 2' }
      ]
      fincas.pagination.value.totalItems = 2
    })

    it('should remove finca from list', async () => {
      deleteFinca.mockResolvedValue()

      await fincas.remove(1)

      expect(fincas.fincas.value).toHaveLength(1)
      expect(fincas.fincas.value[0].id).toBe(2)
    })

    it('should clear current finca if deleted', async () => {
      fincas.currentFinca.value = { id: 1, name: 'Finca 1' }
      deleteFinca.mockResolvedValue()

      await fincas.remove(1)

      expect(fincas.currentFinca.value).toBe(null)
    })

    it('should update pagination totalItems on delete', async () => {
      deleteFinca.mockResolvedValue()

      await fincas.remove(1)

      expect(fincas.pagination.value.totalItems).toBe(1)
    })

    it('should not go below 0 in totalItems', async () => {
      fincas.fincas.value = []
      fincas.pagination.value.totalItems = 0
      deleteFinca.mockResolvedValue()

      await fincas.remove(1)

      expect(fincas.pagination.value.totalItems).toBe(0)
    })

    it('should call onFincaDelete callback', async () => {
      const onFincaDelete = vi.fn()
      const fincasWithCallback = useFincas({ onFincaDelete })
      deleteFinca.mockResolvedValue()

      await fincasWithCallback.remove(1)

      expect(onFincaDelete).toHaveBeenCalledWith(1)
    })

    it('should handle delete error', async () => {
      const error = new Error('Delete failed')
      deleteFinca.mockRejectedValue(error)

      await expect(fincas.remove(1)).rejects.toThrow()
      expect(fincas.error.value).toBeTruthy()
    })
  })

  describe('reset', () => {
    it('should reset all state', () => {
      fincas.fincas.value = [{ id: 1 }]
      fincas.currentFinca.value = { id: 1 }
      fincas.isLoading.value = true
      fincas.error.value = 'Error'
      fincas.filters.value = { search: 'test' }
      fincas.pagination.value = {
        currentPage: 2,
        totalPages: 3,
        totalItems: 50,
        itemsPerPage: 20
      }

      fincas.reset()

      expect(fincas.fincas.value).toEqual([])
      expect(fincas.currentFinca.value).toBe(null)
      expect(fincas.isLoading.value).toBe(false)
      expect(fincas.error.value).toBe(null)
      expect(fincas.filters.value).toEqual({})
      expect(fincas.pagination.value).toEqual({
        currentPage: 1,
        totalPages: 1,
        totalItems: 0,
        itemsPerPage: 20
      })
    })
  })

  describe('clearError', () => {
    it('should clear error', () => {
      fincas.error.value = 'Error message'
      fincas.clearError()
      expect(fincas.error.value).toBe(null)
    })
  })

  describe('loadFinca error handling', () => {
    it('should handle loadFinca error', async () => {
      const error = new Error('Load failed')
      getFincaById.mockRejectedValue(error)

      await expect(fincas.loadFinca(1)).rejects.toThrow()
      expect(fincas.error.value).toBeTruthy()
      expect(fincas.isLoading.value).toBe(false)
    })
  })

  describe('loadFincas with filters', () => {
    it('should load fincas with filters', async () => {
      const mockResponse = {
        results: [{ id: 1, name: 'Finca 1' }],
        count: 1
      }
      getFincas.mockResolvedValue(mockResponse)
      fincas.setFilters({ search: 'test' })

      await fincas.loadFincas(fincas.filters.value)

      expect(getFincas).toHaveBeenCalledWith(
        expect.objectContaining({ search: 'test' })
      )
    })
  })

  describe('update finca not in list', () => {
    it('should not throw if finca not in list', async () => {
      fincas.fincas.value = []
      const updatedFinca = { id: 1, name: 'Updated Name' }
      updateFinca.mockResolvedValue(updatedFinca)

      await expect(fincas.update(1, { name: 'Updated Name' })).resolves.toEqual(updatedFinca)
    })
  })
})


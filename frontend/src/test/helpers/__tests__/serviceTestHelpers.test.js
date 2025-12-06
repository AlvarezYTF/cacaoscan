/**
 * Tests for service test helpers
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createServiceTestPattern } from '../serviceTestHelpers'

describe('serviceTestHelpers', () => {
  let mockApi
  let mockService
  let testPattern

  beforeEach(() => {
    mockApi = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn()
    }

    mockService = {
      getItem: vi.fn(),
      createItem: vi.fn(),
      updateItem: vi.fn(),
      deleteItem: vi.fn()
    }

    testPattern = createServiceTestPattern(mockService, {
      mockApi
    })
  })

  describe('testGetSuccess', () => {
    it('should test successful GET operation', async () => {
      const expectedResponse = { id: 1, name: 'Test' }
      const params = { id: 1 }
      const expectedPath = '/api/items/'

      mockService.getItem.mockImplementation(async (p) => {
        const response = await mockApi.get(expectedPath, { params: p })
        return response.data
      })

      await testPattern.testGetSuccess('getItem', params, expectedResponse, expectedPath)

      expect(mockApi.get).toHaveBeenCalledWith(expectedPath, { params })
    })
  })

  describe('testGetError', () => {
    it('should test error handling for GET operation', async () => {
      const error = new Error('Network error')
      const params = { id: 1 }

      mockService.getItem.mockImplementation(async () => {
        throw error
      })

      await testPattern.testGetError('getItem', params, error)

      expect(mockService.getItem).toHaveBeenCalled()
    })
  })

  describe('testPostSuccess', () => {
    it('should test successful POST operation', async () => {
      const data = { name: 'Test' }
      const expectedResponse = { id: 1, name: 'Test' }
      const expectedPath = '/api/items/'

      mockService.createItem.mockImplementation(async (d) => {
        const response = await mockApi.post(expectedPath, d)
        return response.data
      })

      await testPattern.testPostSuccess('createItem', data, expectedResponse, expectedPath)

      expect(mockApi.post).toHaveBeenCalledWith(expectedPath, data)
    })
  })

  describe('testPostError', () => {
    it('should test error handling for POST operation', async () => {
      const error = new Error('Validation error')
      const data = { name: 'Test' }

      mockService.createItem.mockImplementation(async () => {
        throw error
      })

      await testPattern.testPostError('createItem', data, error)

      expect(mockService.createItem).toHaveBeenCalled()
    })
  })

  describe('testPutSuccess', () => {
    it('should test successful PUT operation', async () => {
      const id = 1
      const data = { name: 'Updated' }
      const expectedResponse = { id: 1, name: 'Updated' }
      const expectedPath = `/api/items/${id}/`

      mockService.updateItem.mockImplementation(async (i, d) => {
        const response = await mockApi.put(expectedPath, d)
        return response.data
      })

      await testPattern.testPutSuccess('updateItem', id, data, expectedResponse, expectedPath)

      expect(mockApi.put).toHaveBeenCalledWith(expectedPath, data)
    })
  })

  describe('testPutError', () => {
    it('should test error handling for PUT operation', async () => {
      const error = new Error('Not found')
      const id = 1
      const data = { name: 'Updated' }

      mockService.updateItem.mockImplementation(async () => {
        throw error
      })

      await testPattern.testPutError('updateItem', id, data, error)

      expect(mockService.updateItem).toHaveBeenCalled()
    })
  })

  describe('testDeleteSuccess', () => {
    it('should test successful DELETE operation', async () => {
      const id = 1
      const expectedResponse = { success: true }
      const expectedPath = `/api/items/${id}/`

      mockService.deleteItem.mockImplementation(async (i) => {
        const response = await mockApi.delete(expectedPath)
        return response.data
      })

      await testPattern.testDeleteSuccess('deleteItem', id, expectedResponse, expectedPath)

      expect(mockApi.delete).toHaveBeenCalledWith(expectedPath)
    })
  })

  describe('testDeleteError', () => {
    it('should test error handling for DELETE operation', async () => {
      const error = new Error('Forbidden')
      const id = 1

      mockService.deleteItem.mockImplementation(async () => {
        throw error
      })

      await testPattern.testDeleteError('deleteItem', id, error)

      expect(mockService.deleteItem).toHaveBeenCalled()
    })
  })
})


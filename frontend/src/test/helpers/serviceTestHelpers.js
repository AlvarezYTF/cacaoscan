/**
 * Test helpers for service tests
 * Provides reusable patterns for testing services
 */

import { vi } from 'vitest'

/**
 * Creates a test pattern for CRUD operations
 * @param {Object} service - Service object to test
 * @param {Object} options - Test options
 * @returns {Object} Test patterns
 */
export function createServiceTestPattern(service, options = {}) {
  const {
    serviceName = 'service',
    basePath = '/',
    mockApi
  } = options

  return {
    /**
     * Tests successful GET operation
     * @param {string} methodName - Method name to test
     * @param {Object} params - Parameters for the method
     * @param {Object} expectedResponse - Expected response
     * @param {string} expectedPath - Expected API path
     */
    testGetSuccess: async (methodName, params, expectedResponse, expectedPath) => {
      mockApi.get.mockResolvedValue({ data: expectedResponse })
      const result = await service[methodName](params)
      expect(mockApi.get).toHaveBeenCalledWith(expectedPath, { params })
      expect(result).toBeDefined()
    },

    /**
     * Tests error handling for GET operation
     * @param {string} methodName - Method name to test
     * @param {Object} params - Parameters for the method
     * @param {Error} error - Error to throw
     */
    testGetError: async (methodName, params, error) => {
      mockApi.get.mockRejectedValue(error)
      await expect(service[methodName](params)).rejects.toThrow(error.message)
    },

    /**
     * Tests successful POST operation
     * @param {string} methodName - Method name to test
     * @param {Object} data - Data to send
     * @param {Object} expectedResponse - Expected response
     * @param {string} expectedPath - Expected API path
     */
    testPostSuccess: async (methodName, data, expectedResponse, expectedPath) => {
      mockApi.post.mockResolvedValue({ data: expectedResponse })
      const result = await service[methodName](data)
      expect(mockApi.post).toHaveBeenCalledWith(expectedPath, data)
      expect(result).toEqual(expectedResponse)
    },

    /**
     * Tests error handling for POST operation
     * @param {string} methodName - Method name to test
     * @param {Object} data - Data to send
     * @param {Error} error - Error to throw
     */
    testPostError: async (methodName, data, error) => {
      mockApi.post.mockRejectedValue(error)
      await expect(service[methodName](data)).rejects.toThrow(error.message)
    },

    /**
     * Tests successful PUT operation
     * @param {string} methodName - Method name to test
     * @param {number} id - Resource ID
     * @param {Object} data - Data to update
     * @param {Object} expectedResponse - Expected response
     * @param {string} expectedPath - Expected API path
     */
    testPutSuccess: async (methodName, id, data, expectedResponse, expectedPath) => {
      mockApi.put.mockResolvedValue({ data: expectedResponse })
      const result = await service[methodName](id, data)
      expect(mockApi.put).toHaveBeenCalledWith(expectedPath, data)
      expect(result).toEqual(expectedResponse)
    },

    /**
     * Tests error handling for PUT operation
     * @param {string} methodName - Method name to test
     * @param {number} id - Resource ID
     * @param {Object} data - Data to update
     * @param {Error} error - Error to throw
     */
    testPutError: async (methodName, id, data, error) => {
      mockApi.put.mockRejectedValue(error)
      await expect(service[methodName](id, data)).rejects.toThrow(error.message)
    },

    /**
     * Tests successful DELETE operation
     * @param {string} methodName - Method name to test
     * @param {number} id - Resource ID
     * @param {Object} expectedResponse - Expected response
     * @param {string} expectedPath - Expected API path
     */
    testDeleteSuccess: async (methodName, id, expectedResponse, expectedPath) => {
      mockApi.delete.mockResolvedValue({ data: expectedResponse })
      const result = await service[methodName](id)
      expect(mockApi.delete).toHaveBeenCalledWith(expectedPath)
      expect(result).toEqual(expectedResponse)
    },

    /**
     * Tests error handling for DELETE operation
     * @param {string} methodName - Method name to test
     * @param {number} id - Resource ID
     * @param {Error} error - Error to throw
     */
    testDeleteError: async (methodName, id, error) => {
      mockApi.delete.mockRejectedValue(error)
      await expect(service[methodName](id)).rejects.toThrow(error.message)
    }
  }
}


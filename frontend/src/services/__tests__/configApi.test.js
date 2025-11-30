import { describe, it, expect, beforeEach, vi } from 'vitest'
import api from '../api'
import configApi from '../configApi'

vi.mock('../api', () => ({
  default: {
    get: vi.fn(),
    put: vi.fn()
  }
}))

describe('configApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getGeneralConfig', () => {
    it('should get general config successfully', async () => {
      const mockResponse = {
        data: { setting1: 'value1', setting2: 'value2' }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await configApi.getGeneralConfig()

      expect(api.get).toHaveBeenCalledWith('/config/general/')
      expect(result).toEqual(mockResponse.data)
    })

    it('should return null on 500 error', async () => {
      const error = {
        response: {
          status: 500
        }
      }
      api.get.mockRejectedValue(error)

      const result = await configApi.getGeneralConfig()

      expect(result).toBe(null)
    })

    it('should return null on 403 error', async () => {
      const error = {
        response: {
          status: 403
        }
      }
      api.get.mockRejectedValue(error)

      const result = await configApi.getGeneralConfig()

      expect(result).toBe(null)
    })

    it('should throw error on other errors', async () => {
      const error = new Error('Network error')
      api.get.mockRejectedValue(error)

      await expect(configApi.getGeneralConfig()).rejects.toThrow('Network error')
    })
  })

  describe('saveGeneralConfig', () => {
    it('should save general config successfully', async () => {
      const configData = { setting1: 'newvalue' }
      const mockResponse = {
        data: configData
      }
      api.put.mockResolvedValue(mockResponse)

      const result = await configApi.saveGeneralConfig(configData)

      expect(api.put).toHaveBeenCalledWith('/config/general/', configData)
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when saving config', async () => {
      const error = new Error('Save error')
      api.put.mockRejectedValue(error)

      await expect(configApi.saveGeneralConfig({})).rejects.toThrow('Save error')
    })
  })

  describe('getSecurityConfig', () => {
    it('should get security config successfully', async () => {
      const mockResponse = {
        data: { min_password_length: 8 }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await configApi.getSecurityConfig()

      expect(api.get).toHaveBeenCalledWith('/config/security/')
      expect(result).toEqual(mockResponse.data)
    })

    it('should return null on 403 or 500 error', async () => {
      const error = {
        response: {
          status: 403
        }
      }
      api.get.mockRejectedValue(error)

      const result = await configApi.getSecurityConfig()

      expect(result).toBe(null)
    })
  })

  describe('saveSecurityConfig', () => {
    it('should save security config successfully', async () => {
      const configData = { min_password_length: 10 }
      const mockResponse = {
        data: configData
      }
      api.put.mockResolvedValue(mockResponse)

      const result = await configApi.saveSecurityConfig(configData)

      expect(api.put).toHaveBeenCalledWith('/config/security/', configData)
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('getMLConfig', () => {
    it('should get ML config successfully', async () => {
      const mockResponse = {
        data: { model_version: '1.0' }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await configApi.getMLConfig()

      expect(api.get).toHaveBeenCalledWith('/config/ml/')
      expect(result).toEqual(mockResponse.data)
    })

    it('should return null on 403 or 500 error', async () => {
      const error = {
        response: {
          status: 500
        }
      }
      api.get.mockRejectedValue(error)

      const result = await configApi.getMLConfig()

      expect(result).toBe(null)
    })
  })

  describe('saveMLConfig', () => {
    it('should save ML config successfully', async () => {
      const configData = { model_version: '2.0' }
      const mockResponse = {
        data: configData
      }
      api.put.mockResolvedValue(mockResponse)

      const result = await configApi.saveMLConfig(configData)

      expect(api.put).toHaveBeenCalledWith('/config/ml/', configData)
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('getSystemConfig', () => {
    it('should get system config successfully', async () => {
      const mockResponse = {
        data: {
          version: '1.0.0',
          server_status: 'online'
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await configApi.getSystemConfig()

      expect(api.get).toHaveBeenCalledWith('/config/system/')
      expect(result).toEqual(mockResponse.data)
    })

    it('should return default values on 500 or 403 error', async () => {
      const error = {
        response: {
          status: 500
        }
      }
      api.get.mockRejectedValue(error)

      const result = await configApi.getSystemConfig()

      expect(result).toEqual({
        version: '1.0.0',
        server_status: 'online',
        backend_version: '4.2.7',
        frontend_version: '3.5.3',
        database: 'PostgreSQL 16'
      })
    })

    it('should throw error on other errors', async () => {
      const error = new Error('Network error')
      api.get.mockRejectedValue(error)

      await expect(configApi.getSystemConfig()).rejects.toThrow('Network error')
    })
  })
})


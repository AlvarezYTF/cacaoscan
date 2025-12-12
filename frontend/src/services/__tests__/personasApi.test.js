import { describe, it, expect, beforeEach, vi } from 'vitest'
import api from '../api'
import { personasApi } from '../personasApi'

vi.mock('../api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn()
  }
}))

describe('personasApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getPerfil', () => {
    it('should get profile successfully', async () => {
      const mockResponse = {
        data: {
          id: 1,
          primer_nombre: 'Juan',
          primer_apellido: 'Pérez',
          email: 'juan@example.com'
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await personasApi.getPerfil()

      expect(api.get).toHaveBeenCalledWith('/personas/perfil/', { params: {} })
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when getting profile', async () => {
      const error = new Error('Network error')
      api.get.mockRejectedValue(error)

      await expect(personasApi.getPerfil()).rejects.toThrow('Network error')
    })
  })

  describe('crearPerfil', () => {
    it('should create profile successfully', async () => {
      const profileData = {
        primer_nombre: 'Juan',
        primer_apellido: 'Pérez',
        tipo_documento: 'CC',
        numero_documento: '1234567890'
      }
      const mockResponse = {
        data: { id: 1, ...profileData }
      }
      api.post.mockResolvedValue(mockResponse)

      const result = await personasApi.crearPerfil(profileData)

      expect(api.post).toHaveBeenCalledWith('/personas/perfil/', profileData, {})
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when creating profile', async () => {
      const error = new Error('Validation error')
      api.post.mockRejectedValue(error)

      await expect(personasApi.crearPerfil({})).rejects.toThrow('Validation error')
    })
  })

  describe('actualizarPerfil', () => {
    it('should update profile successfully', async () => {
      const profileData = {
        primer_nombre: 'Juan Updated',
        telefono: '1234567890'
      }
      const mockResponse = {
        data: { id: 1, ...profileData }
      }
      api.patch.mockResolvedValue(mockResponse)

      const result = await personasApi.actualizarPerfil(profileData)

      expect(api.patch).toHaveBeenCalledWith('/personas/perfil/', profileData, {})
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when updating profile', async () => {
      const error = new Error('Update error')
      api.patch.mockRejectedValue(error)

      await expect(personasApi.actualizarPerfil({})).rejects.toThrow('Update error')
    })
  })

  describe('getPersonaByUserId', () => {
    it('should get persona by user id successfully', async () => {
      const mockResponse = {
        data: {
          id: 1,
          usuario: 1,
          primer_nombre: 'Juan',
          primer_apellido: 'Pérez'
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await personasApi.getPersonaByUserId(1)

      expect(api.get).toHaveBeenCalledWith('/personas/admin/1/', { params: {} })
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when getting persona by user id', async () => {
      const error = new Error('Not found')
      api.get.mockRejectedValue(error)

      await expect(personasApi.getPersonaByUserId(999)).rejects.toThrow('Not found')
    })
  })

  describe('updatePersonaByUserId', () => {
    it('should update persona by user id successfully', async () => {
      const personaData = {
        primer_nombre: 'Juan Updated',
        telefono: '1234567890'
      }
      const mockResponse = {
        data: { id: 1, usuario: 1, ...personaData }
      }
      api.patch.mockResolvedValue(mockResponse)

      const result = await personasApi.updatePersonaByUserId(1, personaData)

      expect(api.patch).toHaveBeenCalledWith('/personas/admin/1/', personaData, {})
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle error when updating persona by user id', async () => {
      const error = new Error('Update error')
      api.patch.mockRejectedValue(error)

      await expect(personasApi.updatePersonaByUserId(1, {})).rejects.toThrow('Update error')
    })
  })
})


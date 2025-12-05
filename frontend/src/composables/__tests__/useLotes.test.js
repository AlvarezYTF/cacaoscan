/**
 * Unit tests for useLotes composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useLotes } from '../useLotes.js'
import * as lotesApi from '@/services/lotesApi'

// Mock dependencies
const mockAuthStore = {
  user: { id: 1 },
  userRole: 'farmer'
}

const mockNotificationStore = {
  addNotification: vi.fn()
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => mockNotificationStore
}))

vi.mock('@/services/lotesApi', () => ({
  getLotes: vi.fn(),
  getLoteById: vi.fn(),
  createLote: vi.fn(),
  updateLote: vi.fn(),
  deleteLote: vi.fn(),
  getLoteStats: vi.fn(),
  getVariedadesCacao: vi.fn(),
  getEstadosLote: vi.fn(),
  validateLoteData: vi.fn(),
  formatLoteData: vi.fn()
}))

vi.mock('@/services/fincasApi', () => ({
  getFincaById: vi.fn()
}))

describe('useLotes', () => {
  let lotes
  let fincasApi

  beforeEach(async () => {
    vi.clearAllMocks()
    mockAuthStore.userRole = 'farmer'
    fincasApi = await import('@/services/fincasApi')
    fincasApi.getFincaById.mockClear()
    lotes = useLotes()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(lotes.loading.value).toBe(false)
      expect(lotes.error.value).toBe(null)
      expect(lotes.lote.value).toBe(null)
      expect(lotes.lotes.value).toEqual([])
    })
  })

  describe('permissions', () => {
    it('should allow admin to edit any lote', () => {
      mockAuthStore.userRole = 'admin'
      
      // Re-create to get new computed
      const newLotes = useLotes()
      const loteData = { id: 1 }
      
      expect(newLotes.canEdit(loteData)).toBe(true)
    })

    it('should allow farmer to edit own lote', () => {
      const loteData = {
        id: 1,
        finca: {
          agricultor: 1
        }
      }
      
      expect(lotes.canEdit(loteData)).toBe(true)
    })

    it('should not allow farmer to edit other lote', () => {
      const loteData = {
        id: 1,
        finca: {
          agricultor: 2
        }
      }
      
      expect(lotes.canEdit(loteData)).toBe(false)
    })
  })

  describe('loadLotes', () => {
    it('should load lotes successfully', async () => {
      const mockData = [{ id: 1, name: 'Lote 1' }]
      lotesApi.getLotes.mockResolvedValue(mockData)

      await lotes.loadLotes()

      expect(lotesApi.getLotes).toHaveBeenCalled()
      expect(lotes.lotes.value).toEqual(mockData)
      expect(lotes.loading.value).toBe(false)
    })

    it('should handle error correctly', async () => {
      const error = new Error('Network error')
      lotesApi.getLotes.mockRejectedValue(error)

      await expect(lotes.loadLotes()).rejects.toThrow()

      expect(lotes.error.value).toBeTruthy()
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })
  })

  describe('loadLote', () => {
    it('should load single lote', async () => {
      const mockLote = { id: 1, name: 'Lote 1' }
      lotesApi.getLoteById.mockResolvedValue(mockLote)

      await lotes.loadLote(1)

      expect(lotesApi.getLoteById).toHaveBeenCalledWith(1)
      expect(lotes.lote.value).toEqual(mockLote)
    })

    it('should load finca when included in lote', async () => {
      const mockLote = { id: 1, finca: { id: 1, nombre: 'Finca 1' } }
      lotesApi.getLoteById.mockResolvedValue(mockLote)

      await lotes.loadLote(1)

      expect(lotes.finca.value).toEqual(mockLote.finca)
    })

    it('should load finca separately when only ID provided', async () => {
      const mockLote = { id: 1, finca: 1 }
      const mockFinca = { id: 1, nombre: 'Finca 1' }
      lotesApi.getLoteById.mockResolvedValue(mockLote)
      
      const fincasApi = await import('@/services/fincasApi')
      fincasApi.getFincaById.mockResolvedValue(mockFinca)

      await lotes.loadLote(1)

      expect(fincasApi.getFincaById).toHaveBeenCalledWith(1)
    })

    it('should handle error loading lote', async () => {
      const error = new Error('Load error')
      lotesApi.getLoteById.mockRejectedValue(error)

      await expect(lotes.loadLote(1)).rejects.toThrow()
      expect(lotes.error.value).toBeTruthy()
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })
  })

  describe('loadFinca', () => {
    it('should load finca successfully', async () => {
      const mockFinca = { id: 1, nombre: 'Finca 1' }
      const fincasApi = await import('@/services/fincasApi')
      fincasApi.getFincaById.mockResolvedValue(mockFinca)

      const result = await lotes.loadFinca(1)

      expect(lotes.finca.value).toEqual(mockFinca)
      expect(result).toEqual(mockFinca)
    })

    it('should handle error loading finca', async () => {
      const error = new Error('Finca error')
      const fincasApi = await import('@/services/fincasApi')
      fincasApi.getFincaById.mockRejectedValue(error)

      await expect(lotes.loadFinca(1)).rejects.toThrow()
    })
  })

  describe('createLote', () => {
    it('should create lote successfully', async () => {
      const loteData = { nombre: 'Lote 1', finca: 1 }
      const mockResult = { id: 1, ...loteData }
      lotesApi.validateLoteData.mockReturnValue({ isValid: true, errors: [] })
      lotesApi.formatLoteData.mockReturnValue(loteData)
      lotesApi.createLote.mockResolvedValue(mockResult)

      const result = await lotes.createLote(loteData)

      expect(lotesApi.validateLoteData).toHaveBeenCalled()
      expect(lotesApi.formatLoteData).toHaveBeenCalled()
      expect(lotesApi.createLote).toHaveBeenCalled()
      expect(result).toEqual(mockResult)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })

    it('should handle validation error', async () => {
      const loteData = { nombre: '' }
      lotesApi.validateLoteData.mockReturnValue({
        isValid: false,
        errors: ['Nombre requerido']
      })

      await expect(lotes.createLote(loteData)).rejects.toThrow()
    })

    it('should handle create error', async () => {
      const loteData = { nombre: 'Lote 1' }
      lotesApi.validateLoteData.mockReturnValue({ isValid: true, errors: [] })
      lotesApi.formatLoteData.mockReturnValue(loteData)
      const error = new Error('Create error')
      lotesApi.createLote.mockRejectedValue(error)

      await expect(lotes.createLote(loteData)).rejects.toThrow()
      expect(lotes.error.value).toBeTruthy()
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })
  })

  describe('updateLote', () => {
    it('should update lote successfully', async () => {
      const loteData = { nombre: 'Lote Updated' }
      const mockResult = { id: 1, ...loteData }
      lotesApi.validateLoteData.mockReturnValue({ isValid: true, errors: [] })
      lotesApi.formatLoteData.mockReturnValue(loteData)
      lotesApi.updateLote.mockResolvedValue(mockResult)
      lotes.lote.value = { id: 1 }

      await lotes.updateLote(1, loteData)

      expect(lotesApi.updateLote).toHaveBeenCalledWith(1, loteData)
      expect(lotes.lote.value).toEqual(mockResult)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })

    it('should handle update error', async () => {
      const loteData = { nombre: 'Lote Updated' }
      lotesApi.validateLoteData.mockReturnValue({ isValid: true, errors: [] })
      lotesApi.formatLoteData.mockReturnValue(loteData)
      const error = new Error('Update error')
      lotesApi.updateLote.mockRejectedValue(error)

      await expect(lotes.updateLote(1, loteData)).rejects.toThrow()
      expect(lotes.error.value).toBeTruthy()
    })
  })

  describe('deleteLote', () => {
    it('should delete lote successfully', async () => {
      lotes.lotes.value = [{ id: 1 }, { id: 2 }]
      lotes.lote.value = { id: 1 }
      lotesApi.deleteLote.mockResolvedValue({})

      const result = await lotes.deleteLote(1)

      expect(lotesApi.deleteLote).toHaveBeenCalledWith(1)
      expect(lotes.lotes.value).not.toContainEqual({ id: 1 })
      expect(lotes.lote.value).toBe(null)
      expect(result).toBe(true)
      expect(mockNotificationStore.addNotification).toHaveBeenCalled()
    })

    it('should handle delete error', async () => {
      const error = new Error('Delete error')
      lotesApi.deleteLote.mockRejectedValue(error)

      await expect(lotes.deleteLote(1)).rejects.toThrow()
      expect(lotes.error.value).toBeTruthy()
    })
  })

  describe('loadStats', () => {
    it('should load stats successfully', async () => {
      const mockStats = { total: 10, promedio: 5 }
      vi.spyOn(lotesApi, 'getLoteStats').mockResolvedValue(mockStats)

      const result = await lotes.loadStats(1)

      expect(result).toEqual(mockStats)
    })

    it('should handle stats error', async () => {
      const error = new Error('Stats error')
      vi.spyOn(lotesApi, 'getLoteStats').mockRejectedValue(error)

      await expect(lotes.loadStats(1)).rejects.toThrow()
    })
  })

  describe('loadAnalisis', () => {
    it('should load analisis', async () => {
      lotes.analisis.value = []
      const result = await lotes.loadAnalisis(1)
      expect(result).toEqual([])
    })

    it('should handle analisis error', async () => {
      // Mock the analisis loading to return empty array
      await expect(lotes.loadAnalisis(1)).resolves.toEqual([])
    })
  })

  describe('permissions', () => {
    it('should check canDelete same as canEdit', () => {
      const loteData = { id: 1, finca: { agricultor: 1 } }
      expect(lotes.canDelete(loteData)).toBe(lotes.canEdit(loteData))
    })

    it('should check canView same as canEdit', () => {
      const loteData = { id: 1, finca: { agricultor: 1 } }
      expect(lotes.canView(loteData)).toBe(lotes.canEdit(loteData))
    })

    it('should return false for canEdit when no loteData', () => {
      expect(lotes.canEdit(null)).toBe(false)
      expect(lotes.canEdit(undefined)).toBe(false)
    })

    it('should allow farmer with finca agricultor_id', () => {
      const loteData = {
        id: 1,
        finca: {
          agricultor_id: 1
        }
      }
      expect(lotes.canEdit(loteData)).toBe(true)
    })

    it('should use finca from ref when finca is ID', () => {
      lotes.finca.value = { agricultor: 1 }
      const loteData = {
        id: 1,
        finca: 1
      }
      expect(lotes.canEdit(loteData)).toBe(true)
    })
  })

  describe('clearError', () => {
    it('should clear error', () => {
      lotes.error.value = 'Some error'
      lotes.clearError()
      expect(lotes.error.value).toBe(null)
    })
  })

  describe('computed properties', () => {
    it('should have isAdmin computed', () => {
      mockAuthStore.userRole = 'admin'
      const adminLotes = useLotes()
      expect(adminLotes.isAdmin.value).toBe(true)
    })

    it('should have isFarmer computed', () => {
      expect(lotes.isFarmer.value).toBe(true)
    })

    it('should have isFarmer for agricultor role', () => {
      mockAuthStore.userRole = 'agricultor'
      const agricultorLotes = useLotes()
      expect(agricultorLotes.isFarmer.value).toBe(true)
    })
  })

  describe('API helpers', () => {
    it('should expose getVariedadesCacao', () => {
      expect(lotes.getVariedadesCacao).toBeDefined()
    })

    it('should expose getEstadosLote', () => {
      expect(lotes.getEstadosLote).toBeDefined()
    })

    it('should expose validateLoteData', () => {
      expect(lotes.validateLoteData).toBeDefined()
    })

    it('should expose formatLoteData', () => {
      expect(lotes.formatLoteData).toBeDefined()
    })
  })

  describe('loadLotes with pagination', () => {
    it('should handle paginated response', async () => {
      const mockData = {
        results: [{ id: 1 }, { id: 2 }],
        count: 2
      }
      lotesApi.getLotes.mockResolvedValue(mockData)

      await lotes.loadLotes()

      expect(lotes.lotes.value).toEqual(mockData.results)
    })

    it('should handle array response', async () => {
      const mockData = [{ id: 1 }, { id: 2 }]
      lotesApi.getLotes.mockResolvedValue(mockData)

      await lotes.loadLotes()

      expect(lotes.lotes.value).toEqual(mockData)
    })
  })
})


/**
 * Unit tests for useLotes composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useLotes } from '../useLotes.js'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
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
  getVariedadesCacao: vi.fn(),
  getEstadosLote: vi.fn(),
  validateLoteData: vi.fn(),
  formatLoteData: vi.fn()
}))

describe('useLotes', () => {
  let lotes

  beforeEach(() => {
    vi.clearAllMocks()
    mockAuthStore.userRole = 'farmer'
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

      const result = await lotes.loadLotes()

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

      const result = await lotes.loadLote(1)

      expect(lotesApi.getLoteById).toHaveBeenCalledWith(1)
      expect(lotes.lote.value).toEqual(mockLote)
    })
  })
})


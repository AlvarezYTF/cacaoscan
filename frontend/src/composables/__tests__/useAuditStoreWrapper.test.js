/**
 * Unit tests for useAuditStoreWrapper composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuditStoreWrapper } from '../useAuditStoreWrapper.js'
import { useAuditStore } from '@/stores/audit'

// Mock dependencies
const mockStore = {
  activityLogs: [],
  loginHistory: [],
  stats: {},
  pagination: { currentPage: 1, totalPages: 1 },
  loading: false,
  error: null,
  fetchActivityLogs: vi.fn(),
  exportActivityLogs: vi.fn()
}

vi.mock('@/stores/audit', () => ({
  useAuditStore: () => mockStore
}))

describe('useAuditStoreWrapper', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    wrapper = useAuditStoreWrapper()
  })

  describe('initial state', () => {
    it('should expose store state', () => {
      expect(wrapper.logs.value).toEqual([])
      expect(wrapper.loading.value).toBe(false)
    })
  })

  describe('fetchAuditLogs', () => {
    it('should fetch audit logs with filters', async () => {
      mockStore.fetchActivityLogs.mockResolvedValue()
      
      await wrapper.fetchAuditLogs({
        user: 'testuser',
        action: 'create',
        page: 1
      })

      expect(mockStore.fetchActivityLogs).toHaveBeenCalledWith({
        usuario: 'testuser',
        accion: 'create',
        page: 1
      })
    })
  })

  describe('formatAuditAction', () => {
    it('should format known actions', () => {
      expect(wrapper.formatAuditAction('create')).toBe('Crear')
      expect(wrapper.formatAuditAction('update')).toBe('Actualizar')
      expect(wrapper.formatAuditAction('login')).toBe('Inicio de sesión')
    })

    it('should return original value for unknown action', () => {
      expect(wrapper.formatAuditAction('unknown')).toBe('unknown')
    })
  })

  describe('formatAuditDate', () => {
    it('should format recent date', () => {
      const now = new Date()
      const oneMinuteAgo = new Date(now.getTime() - 60000)
      
      const formatted = wrapper.formatAuditDate(oneMinuteAgo.toISOString())
      
      expect(formatted).toContain('minuto')
    })

    it('should return empty string for null', () => {
      expect(wrapper.formatAuditDate(null)).toBe('')
    })
  })

  describe('getActionCategory', () => {
    it('should categorize actions correctly', () => {
      expect(wrapper.getActionCategory('create')).toBe('create')
      expect(wrapper.getActionCategory('update')).toBe('update')
      expect(wrapper.getActionCategory('delete')).toBe('delete')
      expect(wrapper.getActionCategory('login')).toBe('auth')
    })
  })

  describe('getActionColor', () => {
    it('should return color classes for actions', () => {
      expect(wrapper.getActionColor('create')).toContain('green')
      expect(wrapper.getActionColor('delete')).toContain('red')
      expect(wrapper.getActionColor('update')).toContain('blue')
    })
  })
})


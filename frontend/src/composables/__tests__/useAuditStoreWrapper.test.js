/**
 * Unit tests for useAuditStoreWrapper composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuditStoreWrapper } from '../useAuditStoreWrapper.js'

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

    it('should return default color for unknown category', () => {
      expect(wrapper.getActionColor('unknown_action')).toContain('yellow')
    })
  })

  describe('fetchAuditLogs', () => {
    it('should map all filter parameters', async () => {
      mockStore.fetchActivityLogs.mockResolvedValue()
      
      await wrapper.fetchAuditLogs({
        user: 'testuser',
        action: 'create',
        model: 'User',
        startDate: '2024-01-01',
        endDate: '2024-12-31',
        page: 2,
        pageSize: 50
      })

      expect(mockStore.fetchActivityLogs).toHaveBeenCalledWith({
        usuario: 'testuser',
        accion: 'create',
        modelo: 'User',
        fecha_inicio: '2024-01-01',
        fecha_fin: '2024-12-31',
        page: 2,
        page_size: 50
      })
    })

    it('should work with empty filters', async () => {
      mockStore.fetchActivityLogs.mockResolvedValue()
      
      await wrapper.fetchAuditLogs()

      expect(mockStore.fetchActivityLogs).toHaveBeenCalledWith({})
    })
  })

  describe('exportAuditLogs', () => {
    it('should export with default format', async () => {
      mockStore.exportActivityLogs.mockResolvedValue()
      
      await wrapper.exportAuditLogs()

      expect(mockStore.exportActivityLogs).toHaveBeenCalledWith({
        format: 'json'
      })
    })

    it('should export with custom format', async () => {
      mockStore.exportActivityLogs.mockResolvedValue()
      
      await wrapper.exportAuditLogs({ format: 'csv' })

      expect(mockStore.exportActivityLogs).toHaveBeenCalledWith({
        format: 'csv'
      })
    })

    it('should map all filter parameters for export', async () => {
      mockStore.exportActivityLogs.mockResolvedValue()
      
      await wrapper.exportAuditLogs({
        format: 'xlsx',
        user: 'testuser',
        action: 'create',
        model: 'User',
        startDate: '2024-01-01',
        endDate: '2024-12-31'
      })

      expect(mockStore.exportActivityLogs).toHaveBeenCalledWith({
        format: 'xlsx',
        usuario: 'testuser',
        accion: 'create',
        modelo: 'User',
        fecha_inicio: '2024-01-01',
        fecha_fin: '2024-12-31'
      })
    })
  })

  describe('formatAuditAction', () => {
    it('should format all known actions', () => {
      expect(wrapper.formatAuditAction('create')).toBe('Crear')
      expect(wrapper.formatAuditAction('update')).toBe('Actualizar')
      expect(wrapper.formatAuditAction('delete')).toBe('Eliminar')
      expect(wrapper.formatAuditAction('view')).toBe('Ver')
      expect(wrapper.formatAuditAction('login')).toBe('Inicio de sesión')
      expect(wrapper.formatAuditAction('logout')).toBe('Cierre de sesión')
      expect(wrapper.formatAuditAction('export')).toBe('Exportar')
      expect(wrapper.formatAuditAction('import')).toBe('Importar')
    })
  })

  describe('formatAuditDate', () => {
    it('should format date less than 1 minute ago', () => {
      const now = new Date()
      const thirtySecondsAgo = new Date(now.getTime() - 30000)
      
      const formatted = wrapper.formatAuditDate(thirtySecondsAgo.toISOString())
      
      expect(formatted).toBe('Hace un momento')
    })

    it('should format date 1 minute ago', () => {
      const now = new Date()
      const oneMinuteAgo = new Date(now.getTime() - 60000)
      
      const formatted = wrapper.formatAuditDate(oneMinuteAgo.toISOString())
      
      expect(formatted).toBe('Hace 1 minuto')
    })

    it('should format date multiple minutes ago', () => {
      const now = new Date()
      const fiveMinutesAgo = new Date(now.getTime() - 5 * 60000)
      
      const formatted = wrapper.formatAuditDate(fiveMinutesAgo.toISOString())
      
      expect(formatted).toBe('Hace 5 minutos')
    })

    it('should format date 1 hour ago', () => {
      const now = new Date()
      const oneHourAgo = new Date(now.getTime() - 3600000)
      
      const formatted = wrapper.formatAuditDate(oneHourAgo.toISOString())
      
      expect(formatted).toBe('Hace 1 hora')
    })

    it('should format date multiple hours ago', () => {
      const now = new Date()
      const threeHoursAgo = new Date(now.getTime() - 3 * 3600000)
      
      const formatted = wrapper.formatAuditDate(threeHoursAgo.toISOString())
      
      expect(formatted).toBe('Hace 3 horas')
    })

    it('should format date 1 day ago', () => {
      const now = new Date()
      const oneDayAgo = new Date(now.getTime() - 86400000)
      
      const formatted = wrapper.formatAuditDate(oneDayAgo.toISOString())
      
      expect(formatted).toBe('Hace 1 día')
    })

    it('should format date multiple days ago', () => {
      const now = new Date()
      const threeDaysAgo = new Date(now.getTime() - 3 * 86400000)
      
      const formatted = wrapper.formatAuditDate(threeDaysAgo.toISOString())
      
      expect(formatted).toBe('Hace 3 días')
    })

    it('should format date more than 7 days ago', () => {
      const oldDate = new Date('2024-01-01T10:00:00Z')
      
      const formatted = wrapper.formatAuditDate(oldDate.toISOString())
      
      expect(formatted).toContain('2024')
      expect(formatted).toContain('ene')
    })
  })

  describe('getActionCategory', () => {
    it('should categorize create actions', () => {
      expect(wrapper.getActionCategory('create')).toBe('create')
      expect(wrapper.getActionCategory('add')).toBe('create')
      expect(wrapper.getActionCategory('new')).toBe('create')
      expect(wrapper.getActionCategory('CREATE_USER')).toBe('create')
    })

    it('should categorize update actions', () => {
      expect(wrapper.getActionCategory('update')).toBe('update')
      expect(wrapper.getActionCategory('edit')).toBe('update')
      expect(wrapper.getActionCategory('modify')).toBe('update')
      expect(wrapper.getActionCategory('change')).toBe('update')
    })

    it('should categorize delete actions', () => {
      expect(wrapper.getActionCategory('delete')).toBe('delete')
      expect(wrapper.getActionCategory('remove')).toBe('delete')
      expect(wrapper.getActionCategory('destroy')).toBe('delete')
    })

    it('should categorize view actions', () => {
      expect(wrapper.getActionCategory('view')).toBe('view')
      expect(wrapper.getActionCategory('read')).toBe('view')
      expect(wrapper.getActionCategory('get')).toBe('view')
      expect(wrapper.getActionCategory('list')).toBe('view')
    })

    it('should categorize auth actions', () => {
      expect(wrapper.getActionCategory('login')).toBe('auth')
      expect(wrapper.getActionCategory('logout')).toBe('auth')
      expect(wrapper.getActionCategory('register')).toBe('auth')
      expect(wrapper.getActionCategory('password_reset')).toBe('auth')
    })

    it('should return other for unknown actions', () => {
      expect(wrapper.getActionCategory('unknown_action')).toBe('other')
      expect(wrapper.getActionCategory('random')).toBe('other')
    })

    it('should handle case insensitive actions', () => {
      expect(wrapper.getActionCategory('CREATE')).toBe('create')
      expect(wrapper.getActionCategory('Update')).toBe('update')
      expect(wrapper.getActionCategory('DELETE')).toBe('delete')
    })
  })

  describe('computed properties', () => {
    it('should expose all store state as computed', () => {
      mockStore.activityLogs = [{ id: 1 }]
      mockStore.loginHistory = [{ id: 1 }]
      mockStore.stats = { total: 10 }
      mockStore.pagination = { currentPage: 2 }
      mockStore.loading = true
      mockStore.error = 'Error'

      const newWrapper = useAuditStoreWrapper()

      expect(newWrapper.logs.value).toEqual([{ id: 1 }])
      expect(newWrapper.loginHistory.value).toEqual([{ id: 1 }])
      expect(newWrapper.stats.value).toEqual({ total: 10 })
      expect(newWrapper.pagination.value).toEqual({ currentPage: 2 })
      expect(newWrapper.loading.value).toBe(true)
      expect(newWrapper.error.value).toBe('Error')
    })

    it('should expose store instance', () => {
      expect(wrapper.store).toBe(mockStore)
    })
  })
})


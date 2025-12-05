/**
 * Unit tests for useAudit composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAudit } from '../useAudit.js'
import * as auditApi from '@/services/auditApi'

// Mock dependencies
const mockNotificationStore = {
  addNotification: vi.fn()
}

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => mockNotificationStore
}))

vi.mock('@/services/auditApi', () => ({
  validateDateFilters: vi.fn(() => ({ isValid: true, errors: [] })),
  getActivityLogs: vi.fn(),
  getLoginHistory: vi.fn(),
  getAuditStats: vi.fn(),
  getUserActivitySummary: vi.fn(),
  generateAuditReport: vi.fn(),
  formatActivityLog: vi.fn((log) => log),
  formatLoginHistory: vi.fn((login) => login),
  AUDIT_ACTION_TYPES: {
    LOGIN: 'login',
    LOGOUT: 'logout',
    CREATE: 'create',
    UPDATE: 'update',
    DELETE: 'delete',
    VIEW: 'view',
    DOWNLOAD: 'download',
    UPLOAD: 'upload',
    EXPORT: 'export',
    IMPORT: 'import',
    TRAIN: 'train',
    PREDICT: 'predict'
  },
  AUDIT_SEVERITY_LEVELS: {
    INFO: 'info',
    WARNING: 'warning',
    ERROR: 'error',
    CRITICAL: 'critical'
  },
  AUDIT_CONFIG: {
    LOGS_REFRESH_INTERVAL: 30000,
    DEFAULT_PAGE_SIZE: 50,
    ACTION_COLORS: {
      login: 'blue',
      logout: 'gray',
      create: 'green',
      update: 'yellow',
      delete: 'red',
      view: 'info',
      download: 'purple',
      upload: 'orange',
      export: 'teal',
      import: 'cyan',
      train: 'indigo',
      predict: 'pink'
    },
    ACTION_ICONS: {
      login: 'sign-in-alt',
      logout: 'sign-out-alt',
      create: 'plus-circle',
      update: 'edit',
      delete: 'trash',
      view: 'eye',
      download: 'download',
      upload: 'upload',
      export: 'file-export',
      import: 'file-import',
      train: 'cogs',
      predict: 'brain'
    }
  }
}))

vi.mock('../useDateFormatting', () => ({
  useDateFormatting: () => ({
    formatDate: vi.fn((date) => date),
    formatDateTime: vi.fn((date) => date)
  })
}))

vi.mock('../useAuditHelpers', () => ({
  useAuditHelpers: () => ({
    formatActivityLog: vi.fn((log) => log),
    formatLoginRecord: vi.fn((record) => record)
  })
}))

describe('useAudit', () => {
  let audit

  beforeEach(() => {
    vi.clearAllMocks()
    audit = useAudit()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(audit.loading.value).toBe(false)
      expect(audit.error.value).toBe(null)
      expect(audit.activityLogs.value).toEqual([])
      expect(audit.loginHistory.value).toEqual([])
    })
  })

  describe('loadActivityLogs', () => {
    it('should load activity logs successfully', async () => {
      const mockLogs = [{ id: 1, accion: 'login' }]
      auditApi.getActivityLogs.mockResolvedValue({
        success: true,
        data: {
          results: mockLogs,
          count: 1,
          current_page: 1,
          total_pages: 1,
          page_size: 50
        }
      })

      await audit.loadActivityLogs()

      expect(auditApi.getActivityLogs).toHaveBeenCalled()
      expect(audit.activityLogs.value).toHaveLength(1)
      expect(audit.loading.value).toBe(false)
    })

    it('should handle error when API returns success: false', async () => {
      auditApi.getActivityLogs.mockResolvedValue({
        success: false,
        error: 'API error message'
      })

      await expect(audit.loadActivityLogs()).rejects.toThrow('API error message')

      expect(audit.error.value).toBeTruthy()
      expect(audit.loading.value).toBe(false)
    })

    it('should handle error when API returns success: false without error message', async () => {
      auditApi.getActivityLogs.mockResolvedValue({
        success: false
      })

      await expect(audit.loadActivityLogs()).rejects.toThrow('Error al cargar los logs de actividad')

      expect(audit.error.value).toBeTruthy()
      expect(audit.loading.value).toBe(false)
    })

    it('should handle error', async () => {
      const error = new Error('Network error')
      auditApi.getActivityLogs.mockRejectedValue(error)

      await expect(audit.loadActivityLogs()).rejects.toThrow()

      expect(audit.error.value).toBeTruthy()
      expect(audit.loading.value).toBe(false)
    })
  })

  describe('loadLoginHistory', () => {
    it('should load login history successfully', async () => {
      const mockHistory = [{ id: 1, exitoso: true }]
      auditApi.getLoginHistory.mockResolvedValue({
        success: true,
        data: {
          results: mockHistory,
          count: 1,
          current_page: 1,
          total_pages: 1,
          page_size: 50
        }
      })

      await audit.loadLoginHistory()

      expect(auditApi.getLoginHistory).toHaveBeenCalled()
      expect(audit.loginHistory.value).toHaveLength(1)
    })
  })

  describe('loadStats', () => {
    it('should load audit stats', async () => {
      const mockStats = {
        total_activities: 100,
        total_logins: 50
      }
      auditApi.getAuditStats.mockResolvedValue({
        success: true,
        data: mockStats
      })

      await audit.loadStats()

      expect(auditApi.getAuditStats).toHaveBeenCalled()
      expect(audit.stats.value).toEqual(mockStats)
    })
  })

  describe('computed properties', () => {
    it('should compute hasActivityFilters', () => {
      audit.activityFilters.usuario = 'test'
      
      expect(audit.hasActivityFilters.value).toBe(true)
      
      audit.activityFilters.usuario = ''
      expect(audit.hasActivityFilters.value).toBe(false)
    })

    it('should compute hasActivityFilters with accion', () => {
      audit.activityFilters.accion = 'login'
      expect(audit.hasActivityFilters.value).toBe(true)
    })

    it('should compute hasActivityFilters with fecha_desde', () => {
      audit.activityFilters.fecha_desde = '2024-01-01'
      expect(audit.hasActivityFilters.value).toBe(true)
    })

    it('should compute hasActivityFilters with fecha_hasta', () => {
      audit.activityFilters.fecha_hasta = '2024-12-31'
      expect(audit.hasActivityFilters.value).toBe(true)
    })

    it('should compute hasLoginFilters', () => {
      audit.loginFilters.usuario = 'test'
      expect(audit.hasLoginFilters.value).toBe(true)
      
      audit.loginFilters.usuario = ''
      audit.loginFilters.exitoso = true
      expect(audit.hasLoginFilters.value).toBe(true)
    })

    it('should compute hasLoginFilters with fecha_desde', () => {
      audit.loginFilters.fecha_desde = '2024-01-01'
      expect(audit.hasLoginFilters.value).toBe(true)
    })

    it('should compute hasLoginFilters with fecha_hasta', () => {
      audit.loginFilters.fecha_hasta = '2024-12-31'
      expect(audit.hasLoginFilters.value).toBe(true)
    })
  })

  describe('loadActivityLogs edge cases', () => {
    it('should handle validation errors', async () => {
      auditApi.validateDateFilters.mockReturnValueOnce({
        isValid: false,
        errors: ['Invalid date range']
      })

      await expect(audit.loadActivityLogs()).rejects.toThrow('Invalid date range')
    })

    it('should handle empty results', async () => {
      auditApi.getActivityLogs.mockResolvedValue({
        success: true,
        data: {
          results: [],
          count: 0,
          current_page: 1,
          total_pages: 1,
          page_size: 50
        }
      })

      await audit.loadActivityLogs()

      expect(audit.activityLogs.value).toEqual([])
    })

    it('should merge params with filters', async () => {
      auditApi.getActivityLogs.mockResolvedValue({
        success: true,
        data: {
          results: [],
          count: 0,
          current_page: 1,
          total_pages: 1,
          page_size: 50
        }
      })

      await audit.loadActivityLogs({ page: 2 })

      expect(auditApi.getActivityLogs).toHaveBeenCalledWith(
        expect.objectContaining({ page: 2 })
      )
    })
  })

  describe('loadLoginHistory edge cases', () => {
    it('should handle validation errors', async () => {
      auditApi.validateDateFilters.mockReturnValueOnce({
        isValid: false,
        errors: ['Invalid date range']
      })

      await expect(audit.loadLoginHistory()).rejects.toThrow('Invalid date range')
    })

    it('should handle empty results', async () => {
      auditApi.getLoginHistory.mockResolvedValue({
        success: true,
        data: {
          results: [],
          count: 0,
          current_page: 1,
          total_pages: 1,
          page_size: 50
        }
      })

      await audit.loadLoginHistory()

      expect(audit.loginHistory.value).toEqual([])
    })
  })

  describe('loadStats edge cases', () => {
    it('should handle error without message', async () => {
      auditApi.getAuditStats.mockResolvedValue({
        success: false
      })

      await expect(audit.loadStats()).rejects.toThrow('Error al cargar las estadísticas de auditoría')
    })
  })

  describe('generateReport', () => {
    it('should generate report successfully', async () => {
      auditApi.generateAuditReport.mockResolvedValue({
        success: true,
        data: { report_id: 1 }
      })

      const result = await audit.generateReport({ period: '7d' })

      expect(auditApi.generateAuditReport).toHaveBeenCalled()
      expect(result).toEqual({ report_id: 1 })
      expect(mockNotificationStore.addNotification).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'success' })
      )
    })

    it('should handle error', async () => {
      auditApi.generateAuditReport.mockResolvedValue({
        success: false,
        error: 'Report generation failed'
      })

      await expect(audit.generateReport({})).rejects.toThrow('Report generation failed')
    })
  })

  describe('getUserActivitySummary', () => {
    it('should get user activity summary', async () => {
      auditApi.getUserActivitySummary.mockResolvedValue({
        success: true,
        data: { total_actions: 10 }
      })

      const result = await audit.getUserActivitySummary(1)

      expect(auditApi.getUserActivitySummary).toHaveBeenCalledWith(1, {})
      expect(result).toEqual({ total_actions: 10 })
    })

    it('should handle error', async () => {
      auditApi.getUserActivitySummary.mockResolvedValue({
        success: false,
        error: 'Failed to get summary'
      })

      await expect(audit.getUserActivitySummary(1)).rejects.toThrow('Failed to get summary')
    })
  })

  describe('filter management', () => {
    it('should apply activity filters', () => {
      audit.applyActivityFilters({
        usuario: 'test',
        accion: 'login'
      })

      expect(audit.activityFilters.usuario).toBe('test')
      expect(audit.activityFilters.accion).toBe('login')
      expect(audit.activityFilters.page).toBe(1)
    })

    it('should clear activity filters', () => {
      audit.activityFilters.usuario = 'test'
      audit.activityFilters.accion = 'login'
      audit.activityFilters.page = 2

      audit.clearActivityFilters()

      expect(audit.activityFilters.usuario).toBe('')
      expect(audit.activityFilters.accion).toBe('')
      expect(audit.activityFilters.page).toBe(1)
    })

    it('should apply login filters', () => {
      audit.applyLoginFilters({
        usuario: 'test',
        exitoso: true
      })

      expect(audit.loginFilters.usuario).toBe('test')
      expect(audit.loginFilters.exitoso).toBe(true)
      expect(audit.loginFilters.page).toBe(1)
    })

    it('should clear login filters', () => {
      audit.loginFilters.usuario = 'test'
      audit.loginFilters.exitoso = true
      audit.loginFilters.page = 2

      audit.clearLoginFilters()

      expect(audit.loginFilters.usuario).toBe('')
      expect(audit.loginFilters.exitoso).toBe(null)
      expect(audit.loginFilters.page).toBe(1)
    })
  })

  describe('formatting helpers', () => {
    it('should format action type', () => {
      expect(audit.formatActionType('login')).toBe('Inicio de sesión')
      expect(audit.formatActionType('logout')).toBe('Cierre de sesión')
      expect(audit.formatActionType('create')).toBe('Crear')
      expect(audit.formatActionType('unknown')).toBe('unknown')
    })

    it('should get action icon', () => {
      expect(audit.getActionIcon('login')).toContain('sign-in-alt')
      expect(audit.getActionIcon('unknown')).toContain('info-circle')
    })

    it('should get action color', () => {
      expect(audit.getActionColor('login')).toContain('blue')
      expect(audit.getActionColor('unknown')).toContain('gray')
    })
  })

  describe('clearError', () => {
    it('should clear error', () => {
      audit.error.value = 'Test error'
      
      audit.clearError()
      
      expect(audit.error.value).toBe(null)
    })
  })
})


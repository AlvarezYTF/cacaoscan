/**
 * Unit tests for useAudit composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAudit } from '../useAudit.js'
import { useNotificationStore } from '@/stores/notifications'
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

      const result = await audit.loadActivityLogs()

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

      const result = await audit.loadLoginHistory()

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
  })
})


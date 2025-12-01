import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuditStore } from '../audit'
import api from '@/services/api'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/utils/fileExportUtils', () => ({
  downloadFileFromResponse: vi.fn()
}))

describe('Audit Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useAuditStore()
    vi.clearAllMocks()
  })

  describe('State and Getters', () => {
    it('should have initial state', () => {
      expect(store.activityLogs).toEqual([])
      expect(store.loginHistory).toEqual([])
      expect(store.stats.activity_log.total_activities).toBe(0)
      expect(store.pagination.currentPage).toBe(1)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('should get activity log by id', () => {
      store.activityLogs = [
        { id: 1, accion: 'CREATE' },
        { id: 2, accion: 'UPDATE' }
      ]

      const log = store.getActivityLogById(1)
      expect(log).toEqual({ id: 1, accion: 'CREATE' })
    })

    it('should get login history by id', () => {
      store.loginHistory = [
        { id: 1, success: true },
        { id: 2, success: false }
      ]

      const login = store.getLoginHistoryById(1)
      expect(login).toEqual({ id: 1, success: true })
    })

    it('should get recent activity logs', () => {
      const now = new Date()
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)

      store.activityLogs = [
        { id: 1, timestamp: now.toISOString() },
        { id: 2, timestamp: yesterday.toISOString() },
        { id: 3, timestamp: now.toISOString() },
        { id: 4, timestamp: now.toISOString() },
        { id: 5, timestamp: now.toISOString() },
        { id: 6, timestamp: now.toISOString() },
        { id: 7, timestamp: now.toISOString() },
        { id: 8, timestamp: now.toISOString() },
        { id: 9, timestamp: now.toISOString() },
        { id: 10, timestamp: now.toISOString() },
        { id: 11, timestamp: now.toISOString() }
      ]

      const recent = store.getRecentActivityLogs(10)
      expect(recent).toHaveLength(10)
    })

    it('should get recent logins', () => {
      const now = new Date()
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)

      store.loginHistory = [
        { id: 1, login_time: now.toISOString() },
        { id: 2, login_time: yesterday.toISOString() },
        { id: 3, login_time: now.toISOString() }
      ]

      const recent = store.getRecentLogins(2)
      expect(recent).toHaveLength(2)
    })

    it('should get failed logins', () => {
      store.loginHistory = [
        { id: 1, success: false },
        { id: 2, success: true },
        { id: 3, success: false }
      ]

      const failed = store.getFailedLogins
      expect(failed).toHaveLength(2)
      expect(failed.every(l => !l.success)).toBe(true)
    })

    it('should get successful logins', () => {
      store.loginHistory = [
        { id: 1, success: true },
        { id: 2, success: false },
        { id: 3, success: true }
      ]

      const successful = store.getSuccessfulLogins
      expect(successful).toHaveLength(2)
      expect(successful.every(l => l.success)).toBe(true)
    })

    it('should get activity logs by user', () => {
      store.activityLogs = [
        { id: 1, usuario: 'user1' },
        { id: 2, usuario: 'user2' },
        { id: 3, usuario: 'user1' }
      ]

      const userLogs = store.getActivityLogsByUser('user1')
      expect(userLogs).toHaveLength(2)
    })

    it('should get logins by user', () => {
      store.loginHistory = [
        { id: 1, usuario: 'user1' },
        { id: 2, usuario: 'user2' },
        { id: 3, usuario: 'user1' }
      ]

      const userLogins = store.getLoginsByUser('user1')
      expect(userLogins).toHaveLength(2)
    })

    it('should get activity logs by action', () => {
      store.activityLogs = [
        { id: 1, accion: 'CREATE' },
        { id: 2, accion: 'UPDATE' },
        { id: 3, accion: 'CREATE' }
      ]

      const createLogs = store.getActivityLogsByAction('CREATE')
      expect(createLogs).toHaveLength(2)
    })

    it('should get activity logs by model', () => {
      store.activityLogs = [
        { id: 1, modelo: 'Finca' },
        { id: 2, modelo: 'Lote' },
        { id: 3, modelo: 'Finca' }
      ]

      const fincaLogs = store.getActivityLogsByModel('Finca')
      expect(fincaLogs).toHaveLength(2)
    })

    it('should get logins by IP', () => {
      // Use TEST-NET-1 reserved IPs (192.0.2.x) - safe for testing, never used in real networks
      const TEST_IP_1 = '192.0.2.10'
      const TEST_IP_2 = '192.0.2.20'

      store.loginHistory = [
        { id: 1, ip_address: TEST_IP_1 },
        { id: 2, ip_address: TEST_IP_2 },
        { id: 3, ip_address: TEST_IP_1 }
      ]

      const ipLogins = store.getLoginsByIP(TEST_IP_1)
      expect(ipLogins).toHaveLength(2)
    })
  })

  describe('Actions', () => {
    it('should fetch activity logs successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, accion: 'CREATE' },
            { id: 2, accion: 'UPDATE' }
          ],
          page: 1,
          total_pages: 1,
          count: 2,
          page_size: 50
        }
      }

      api.get.mockResolvedValue(mockResponse)

      await store.fetchActivityLogs()

      expect(store.activityLogs).toHaveLength(2)
      expect(store.pagination.currentPage).toBe(1)
      expect(store.loading).toBe(false)
    })

    it('should handle fetch activity logs error', async () => {
      const error = {
        response: {
          data: {
            detail: 'Error message'
          }
        }
      }

      api.get.mockRejectedValue(error)

      await expect(store.fetchActivityLogs()).rejects.toEqual(error)
      expect(store.error).toBe('Error message')
      expect(store.loading).toBe(false)
    })

    it('should fetch login history successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, success: true },
            { id: 2, success: false }
          ],
          page: 1,
          total_pages: 1,
          count: 2,
          page_size: 50
        }
      }

      api.get.mockResolvedValue(mockResponse)

      await store.fetchLoginHistory()

      expect(store.loginHistory).toHaveLength(2)
      expect(store.pagination.currentPage).toBe(1)
      expect(store.loading).toBe(false)
    })

    it('should fetch stats', async () => {
      const mockStats = {
        activity_log: {
          total_activities: 100,
          activities_today: 10,
          activities_by_action: {},
          activities_by_model: {},
          top_active_users: []
        },
        login_history: {
          total_logins: 50,
          successful_logins: 45,
          failed_logins: 5,
          success_rate: 90,
          login_stats_by_day: [],
          top_ips: [],
          avg_session_duration_minutes: 30
        }
      }

      const mockResponse = {
        data: mockStats
      }

      api.get.mockResolvedValue(mockResponse)

      const response = await store.fetchStats()

      expect(response.data).toEqual(mockStats)
      expect(store.stats).toEqual(mockStats)
    })

    it('should export audit data', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const mockResponse = {
        data: mockBlob
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await store.exportAuditData({})

      expect(result).toBe(true)
      expect(api.post).toHaveBeenCalledWith('/audit/export/', {}, {
        responseType: 'blob'
      })
    })

    it('should get activity log details', async () => {
      const mockResponse = {
        data: { id: 1, accion: 'CREATE' }
      }

      api.get.mockResolvedValue(mockResponse)

      const response = await store.getActivityLogDetails(1)

      expect(response).toEqual(mockResponse)
      expect(api.get).toHaveBeenCalledWith('/audit/activity-logs/1/')
    })

    it('should get login history details', async () => {
      const mockResponse = {
        data: { id: 1, success: true }
      }

      api.get.mockResolvedValue(mockResponse)

      const response = await store.getLoginHistoryDetails(1)

      expect(response).toEqual(mockResponse)
      expect(api.get).toHaveBeenCalledWith('/audit/login-history/1/')
    })

    it('should get audit summary', async () => {
      const mockResponse = {
        data: { summary: 'test' }
      }

      api.get.mockResolvedValue(mockResponse)

      const response = await store.getAuditSummary({})

      expect(response).toEqual(mockResponse)
    })

    it('should get security alerts', async () => {
      const mockResponse = {
        data: [{ id: 1, type: 'suspicious' }]
      }

      api.get.mockResolvedValue(mockResponse)

      const response = await store.getSecurityAlerts()

      expect(response).toEqual(mockResponse)
    })

    it('should get suspicious activity', async () => {
      const mockResponse = {
        data: [{ id: 1, activity: 'test' }]
      }

      api.get.mockResolvedValue(mockResponse)

      const response = await store.getSuspiciousActivity()

      expect(response).toEqual(mockResponse)
    })

    it('should get audit report', async () => {
      const mockResponse = {
        data: { report: 'test' }
      }

      api.post.mockResolvedValue(mockResponse)

      const response = await store.getAuditReport({})

      expect(response).toEqual(mockResponse)
    })

    it('should clear old logs', async () => {
      const mockResponse = {
        data: { deleted: 10 }
      }

      api.post.mockResolvedValue(mockResponse)

      const response = await store.clearOldLogs(90)

      expect(response).toEqual(mockResponse)
      expect(api.post).toHaveBeenCalledWith('/audit/clear-old-logs/', {
        days_to_keep: 90
      })
    })

    it('should get audit dashboard', async () => {
      const mockResponse = {
        data: { dashboard: 'test' }
      }

      api.get.mockResolvedValue(mockResponse)

      const response = await store.getAuditDashboard()

      expect(response).toEqual(mockResponse)
    })

    it('should add activity log', () => {
      const log = { id: 1, accion: 'CREATE' }
      store.addActivityLog(log)
      expect(store.activityLogs[0]).toEqual(log)
    })

    it('should add login history', () => {
      const login = { id: 1, success: true }
      store.addLoginHistory(login)
      expect(store.loginHistory[0]).toEqual(login)
    })

    it('should update activity log', () => {
      store.activityLogs = [
        { id: 1, accion: 'CREATE' }
      ]

      const updated = { id: 1, accion: 'UPDATE' }
      store.updateActivityLog(updated)

      expect(store.activityLogs[0].accion).toBe('UPDATE')
    })

    it('should update login history', () => {
      store.loginHistory = [
        { id: 1, success: false }
      ]

      const updated = { id: 1, success: true }
      store.updateLoginHistory(updated)

      expect(store.loginHistory[0].success).toBe(true)
    })

    it('should remove activity log', () => {
      store.activityLogs = [
        { id: 1 },
        { id: 2 },
        { id: 3 }
      ]

      store.removeActivityLog(2)

      expect(store.activityLogs).toHaveLength(2)
      expect(store.activityLogs.find(l => l.id === 2)).toBeUndefined()
    })

    it('should remove login history', () => {
      store.loginHistory = [
        { id: 1 },
        { id: 2 },
        { id: 3 }
      ]

      store.removeLoginHistory(2)

      expect(store.loginHistory).toHaveLength(2)
      expect(store.loginHistory.find(l => l.id === 2)).toBeUndefined()
    })

    it('should clear error', () => {
      store.error = 'Some error'
      store.clearError()
      expect(store.error).toBe(null)
    })

    it('should reset store', () => {
      store.activityLogs = [{ id: 1 }]
      store.loginHistory = [{ id: 1 }]
      store.loading = true
      store.error = 'Error'

      store.reset()

      expect(store.activityLogs).toEqual([])
      expect(store.loginHistory).toEqual([])
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.stats.activity_log.total_activities).toBe(0)
    })
  })
})


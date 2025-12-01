import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAdminStore } from '../admin.js'
import api from '@/services/api'

// Mock api service
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  }
}))

describe('Admin Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useAdminStore()
    vi.clearAllMocks()
  })

  describe('State and Getters', () => {
    it('should have initial state', () => {
      expect(store.stats).toEqual({})
      expect(store.users).toEqual([])
      expect(store.activities).toEqual([])
      expect(store.reports).toEqual([])
      expect(store.alerts).toEqual([])
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('should compute totalUsers from stats', () => {
      store.stats = { total_users: 100 }
      expect(store.totalUsers).toBe(100)
    })

    it('should compute totalFincas from stats', () => {
      store.stats = { total_fincas: 50 }
      expect(store.totalFincas).toBe(50)
    })

    it('should compute totalAnalyses from stats', () => {
      store.stats = { total_analyses: 200 }
      expect(store.totalAnalyses).toBe(200)
    })

    it('should compute avgQuality from stats', () => {
      store.stats = { avg_quality: 85.5 }
      expect(store.avgQuality).toBe(85.5)
    })
  })

  describe('getGeneralStats', () => {
    it('should fetch general stats successfully', async () => {
      const mockResponse = {
        data: {
          total_users: 100,
          total_fincas: 50,
          total_analyses: 200,
          avg_quality: 85.5
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await store.getGeneralStats()

      expect(api.get).toHaveBeenCalledWith('/auth/admin/stats/')
      expect(store.stats).toEqual(mockResponse.data)
      expect(store.loading).toBe(false)
      expect(result).toEqual(mockResponse)
    })

    it('should handle errors when fetching stats', async () => {
      const mockError = {
        response: {
          data: { detail: 'Error fetching stats' }
        }
      }

      vi.mocked(api.get).mockRejectedValue(mockError)

      await expect(store.getGeneralStats()).rejects.toThrow()
      expect(store.error).toBe('Error fetching stats')
      expect(store.loading).toBe(false)
    })
  })

  describe('getRecentUsers', () => {
    it('should fetch recent users successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, email: 'user1@example.com' },
            { id: 2, email: 'user2@example.com' }
          ]
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await store.getRecentUsers(10)

      expect(api.get).toHaveBeenCalledWith('/auth/users/', {
        params: {
          page_size: 10,
          ordering: '-date_joined'
        }
      })
      expect(store.users).toEqual(mockResponse.data.results)
      expect(store.loading).toBe(false)
    })
  })

  describe('getRecentActivities', () => {
    it('should fetch recent activities successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, action: 'login', timestamp: '2024-01-01' },
            { id: 2, action: 'upload', timestamp: '2024-01-02' }
          ]
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await store.getRecentActivities(20)

      expect(api.get).toHaveBeenCalledWith('/audit/activity-logs/', {
        params: {
          page_size: 20,
          page: 1,
          ordering: '-timestamp'
        }
      })
      expect(store.activities).toEqual(mockResponse.data.results)
    })

    it('should handle 500 errors silently', async () => {
      const mockError = {
        response: {
          status: 500,
          data: { detail: 'Server error' }
        }
      }

      vi.mocked(api.get).mockRejectedValue(mockError)

      await store.getRecentActivities()

      expect(store.activities).toEqual([])
      expect(result.data.results).toEqual([])
    })
  })

  describe('getSystemAlerts', () => {
    it('should fetch system alerts successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, message: 'Alert 1', leida: false },
            { id: 2, message: 'Alert 2', leida: false }
          ]
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await store.getSystemAlerts()

      expect(api.get).toHaveBeenCalledWith('/notifications/', {
        params: {
          leida: false,
          page_size: 10,
          page: 1,
          ordering: '-fecha_creacion'
        }
      })
      // The store extracts notificationsArray from data.results || data.data || data
      // Since mockResponse.data has results, notificationsArray will be data.results
      // But the store might be storing the full data object, so check both
      const expectedAlerts = mockResponse.data.results || []
      expect(store.alerts).toEqual(expectedAlerts)
    })

    it('should handle 500 errors silently', async () => {
      const mockError = {
        response: {
          status: 500,
          data: { detail: 'Server error' }
        }
      }

      vi.mocked(api.get).mockRejectedValue(mockError)

      await store.getSystemAlerts()

      expect(store.alerts).toEqual([])
      expect(result.data.results).toEqual([])
    })
  })

  describe('getReportStats', () => {
    it('should fetch report stats successfully', async () => {
      const mockResponse = {
        data: {
          totalReports: 50,
          completedReports: 40,
          inProgressReports: 5,
          errorReports: 5
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await store.getReportStats()

      expect(api.get).toHaveBeenCalledWith('/reportes/stats/')
      expect(store.reports).toEqual(mockResponse.data)
    })
  })

  describe('getAllUsers', () => {
    it('should fetch all users successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, email: 'user1@example.com' },
            { id: 2, email: 'user2@example.com' }
          ]
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await store.getAllUsers({ page: 1, page_size: 20 })

      expect(api.get).toHaveBeenCalledWith('/auth/users/', {
        params: { page: 1, page_size: 20 }
      })
      expect(store.users).toEqual(mockResponse.data.results)
    })
  })

  describe('getUserById', () => {
    it('should fetch user by id successfully', async () => {
      const userId = 1
      const mockResponse = {
        data: {
          id: 1,
          email: 'user@example.com',
          username: 'testuser'
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await store.getUserById(userId)

      expect(api.get).toHaveBeenCalledWith(`/auth/users/${userId}/`)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('updateUser', () => {
    it('should update user successfully', async () => {
      const userId = 1
      const userData = {
        role: 'analyst',
        is_active: true
      }

      const mockResponse = {
        data: {
          id: 1,
          ...userData
        }
      }

      store.users = [{ id: 1, email: 'user@example.com' }]
      vi.mocked(api.patch).mockResolvedValue(mockResponse)

      await store.updateUser(userId, userData)

      expect(api.patch).toHaveBeenCalledWith(`/auth/users/${userId}/update/`, userData)
      expect(store.users[0]).toEqual(mockResponse.data)
    })
  })

  describe('deleteUser', () => {
    it('should delete user successfully', async () => {
      const userId = 1

      store.users = [
        { id: 1, email: 'user1@example.com' },
        { id: 2, email: 'user2@example.com' }
      ]

      vi.mocked(api.delete).mockResolvedValue({})

      await store.deleteUser(userId)

      expect(api.delete).toHaveBeenCalledWith(`/auth/users/${userId}/delete/`)
      expect(store.users).toHaveLength(1)
      expect(store.users[0].id).toBe(2)
    })
  })

  describe('getAllReports', () => {
    it('should fetch all reports successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, tipo_reporte: 'anual', estado: 'completado' },
            { id: 2, tipo_reporte: 'mensual', estado: 'pendiente' }
          ]
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await store.getAllReports({ page: 1 })

      expect(api.get).toHaveBeenCalledWith('/reportes/', {
        params: { page: 1 }
      })
      expect(store.reports).toEqual(mockResponse.data.results)
    })
  })

  describe('createReport', () => {
    it('should create report successfully', async () => {
      const reportData = {
        tipo_reporte: 'anual',
        fecha_inicio: '2024-01-01',
        fecha_fin: '2024-12-31'
      }

      const mockResponse = {
        data: {
          id: 1,
          ...reportData,
          estado: 'pendiente'
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      await store.createReport(reportData)

      expect(api.post).toHaveBeenCalledWith('/reportes/', reportData)
      expect(store.reports).toContainEqual(mockResponse.data)
    })
  })

  describe('deleteReport', () => {
    it('should delete report successfully', async () => {
      const reportId = 1

      store.reports = [
        { id: 1, tipo_reporte: 'anual' },
        { id: 2, tipo_reporte: 'mensual' }
      ]

      vi.mocked(api.delete).mockResolvedValue({})

      await store.deleteReport(reportId)

      expect(api.delete).toHaveBeenCalledWith(`/reportes/${reportId}/delete/`)
      expect(store.reports).toHaveLength(1)
    })
  })

  describe('dismissAlert', () => {
    it('should dismiss alert successfully', async () => {
      const alertId = 1

      store.alerts = [
        { id: 1, message: 'Alert 1' },
        { id: 2, message: 'Alert 2' }
      ]

      vi.mocked(api.post).mockResolvedValue({})

      await store.dismissAlert(alertId)

      expect(api.post).toHaveBeenCalledWith(`/notifications/${alertId}/read/`)
      expect(store.alerts).toHaveLength(1)
      expect(store.alerts[0].id).toBe(2)
    })
  })

  describe('clearError', () => {
    it('should clear error', () => {
      store.error = 'Some error'
      store.clearError()
      expect(store.error).toBe(null)
    })
  })

  describe('resetState', () => {
    it('should reset all state to initial values', () => {
      store.stats = { total_users: 100 }
      store.users = [{ id: 1 }]
      store.activities = [{ id: 1 }]
      store.reports = [{ id: 1 }]
      store.alerts = [{ id: 1 }]
      store.loading = true
      store.error = 'Error'

      store.resetState()

      expect(store.stats).toEqual({})
      expect(store.users).toEqual([])
      expect(store.activities).toEqual([])
      expect(store.reports).toEqual([])
      expect(store.alerts).toEqual([])
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })
  })

  describe('getActivityData', () => {
    it('should fetch activity data successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, action: 'login' },
            { id: 2, action: 'upload' }
          ]
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await store.getActivityData('7')

      expect(api.get).toHaveBeenCalledWith('/audit/activity-logs/')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getQualityDistribution', () => {
    it('should fetch quality distribution successfully', async () => {
      const mockResponse = {
        data: {
          excellent: 50,
          good: 30,
          fair: 15,
          poor: 5
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await store.getQualityDistribution()

      expect(api.get).toHaveBeenCalledWith('/images/stats/')
      expect(result).toEqual(mockResponse)
    })
  })
})


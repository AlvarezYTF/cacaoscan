import { describe, it, expect, beforeEach, vi } from 'vitest'
import dashboardStatsService from '../dashboardStatsService.js'

// Create mock instance that will be reused using vi.hoisted
const { mockAxiosInstance } = vi.hoisted(() => {
  const instance = {
    interceptors: {
      request: {
        use: vi.fn()
      },
      response: {
        use: vi.fn()
      }
    },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
  return { mockAxiosInstance: instance }
})

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockAxiosInstance)
  }
}))

// Mock apiConfig
vi.mock('@/utils/apiConfig', () => ({
  getApiBaseUrlWithoutPath: vi.fn(() => 'https://test-api.example.com')
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

globalThis.localStorage = localStorageMock

// Mock globalThis.location
globalThis.location = {
  href: 'http://localhost'
}

describe('DashboardStatsService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue('test-token')
    // Reset mockAxiosInstance methods
    mockAxiosInstance.get.mockReset()
    mockAxiosInstance.post.mockReset()
    mockAxiosInstance.put.mockReset()
    mockAxiosInstance.delete.mockReset()
    mockAxiosInstance.interceptors.request.use.mockReset()
    mockAxiosInstance.interceptors.response.use.mockReset()
  })

  describe('getGeneralStats', () => {
    it('should fetch general stats successfully', async () => {
      const mockStats = {
        total_users: 100,
        total_fincas: 50,
        total_lotes: 200
      }

      mockAxiosInstance.get.mockResolvedValue({
        data: mockStats
      })

      const result = await dashboardStatsService.getGeneralStats()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/stats/')
      expect(result).toEqual(mockStats)
    })

    it('should handle error when fetching general stats', async () => {
      const error = new Error('Network error')
      mockAxiosInstance.get.mockRejectedValue(error)

      await expect(dashboardStatsService.getGeneralStats()).rejects.toThrow('Network error')
    })
  })

  describe('getActivityData', () => {
    it('should fetch activity data with default period', async () => {
      const mockActivity = {
        dates: ['2024-01-01', '2024-01-02'],
        values: [10, 20]
      }

      mockAxiosInstance.get.mockResolvedValue({
        data: mockActivity
      })

      const result = await dashboardStatsService.getActivityData()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/activity/?period=30')
      expect(result).toEqual(mockActivity)
    })

    it('should fetch activity data with custom period', async () => {
      const period = '7'
      const mockActivity = {
        dates: ['2024-01-01'],
        values: [5]
      }

      mockAxiosInstance.get.mockResolvedValue({
        data: mockActivity
      })

      const result = await dashboardStatsService.getActivityData(period)

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/activity/?period=7')
      expect(result).toEqual(mockActivity)
    })
  })

  describe('getQualityDistribution', () => {
    it('should fetch quality distribution successfully', async () => {
      const mockDistribution = {
        alta: 40,
        media: 35,
        baja: 25
      }

      mockAxiosInstance.get.mockResolvedValue({
        data: mockDistribution
      })

      const result = await dashboardStatsService.getQualityDistribution()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/quality-distribution/')
      expect(result).toEqual(mockDistribution)
    })
  })

  describe('getRegionStats', () => {
    it('should fetch region stats successfully', async () => {
      const mockRegionStats = [
        { region: 'Guaviare', total: 50 },
        { region: 'Meta', total: 30 }
      ]

      mockAxiosInstance.get.mockResolvedValue({
        data: mockRegionStats
      })

      const result = await dashboardStatsService.getRegionStats()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/region-stats/')
      expect(result).toEqual(mockRegionStats)
    })
  })

  describe('getTrendsData', () => {
    it('should fetch trends data with default parameters', async () => {
      const mockTrends = {
        labels: ['Week 1', 'Week 2'],
        data: [100, 120]
      }

      mockAxiosInstance.get.mockResolvedValue({
        data: mockTrends
      })

      const result = await dashboardStatsService.getTrendsData()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/trends/?period=30&metric=quality')
      expect(result).toEqual(mockTrends)
    })

    it('should fetch trends data with custom parameters', async () => {
      const period = '7'
      const metric = 'production'

      mockAxiosInstance.get.mockResolvedValue({
        data: {}
      })

      await dashboardStatsService.getTrendsData(period, metric)

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/trends/?period=7&metric=production')
    })
  })

  describe('getActiveUsers', () => {
    it('should fetch active users with default limit', async () => {
      const mockUsers = [
        { id: 1, email: 'user1@example.com', activity_count: 50 },
        { id: 2, email: 'user2@example.com', activity_count: 40 }
      ]

      mockAxiosInstance.get.mockResolvedValue({
        data: mockUsers
      })

      const result = await dashboardStatsService.getActiveUsers()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/active-users/?limit=10')
      expect(result).toEqual(mockUsers)
    })

    it('should fetch active users with custom limit', async () => {
      const limit = 20

      mockAxiosInstance.get.mockResolvedValue({
        data: []
      })

      await dashboardStatsService.getActiveUsers(limit)

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/active-users/?limit=20')
    })
  })

  describe('getTopFincas', () => {
    it('should fetch top fincas with default limit', async () => {
      const mockFincas = [
        { id: 1, nombre: 'Finca A', quality_score: 95 },
        { id: 2, nombre: 'Finca B', quality_score: 90 }
      ]

      mockAxiosInstance.get.mockResolvedValue({
        data: mockFincas
      })

      const result = await dashboardStatsService.getTopFincas()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/top-fincas/?limit=10')
      expect(result).toEqual(mockFincas)
    })

    it('should fetch top fincas with custom limit', async () => {
      const limit = 5

      mockAxiosInstance.get.mockResolvedValue({
        data: []
      })

      await dashboardStatsService.getTopFincas(limit)

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/top-fincas/?limit=5')
    })
  })

  describe('getRecentUsers', () => {
    it('should fetch recent users successfully', async () => {
      const mockUsers = [
        { id: 1, email: 'newuser@example.com', created_at: '2024-01-01' }
      ]

      mockAxiosInstance.get.mockResolvedValue({
        data: mockUsers
      })

      const result = await dashboardStatsService.getRecentUsers()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/recent-users/?limit=10')
      expect(result).toEqual(mockUsers)
    })
  })

  describe('getRecentActivities', () => {
    it('should fetch recent activities successfully', async () => {
      const mockActivities = [
        { id: 1, action: 'upload', user: 'user1@example.com', timestamp: '2024-01-01' }
      ]

      mockAxiosInstance.get.mockResolvedValue({
        data: mockActivities
      })

      const result = await dashboardStatsService.getRecentActivities()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/recent-activities/?limit=10')
      expect(result).toEqual(mockActivities)
    })
  })

  describe('getSystemAlerts', () => {
    it('should fetch system alerts successfully', async () => {
      const mockAlerts = [
        { id: 1, type: 'warning', message: 'High error rate' }
      ]

      mockAxiosInstance.get.mockResolvedValue({
        data: mockAlerts
      })

      const result = await dashboardStatsService.getSystemAlerts()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/alerts/')
      expect(result).toEqual(mockAlerts)
    })
  })

  describe('getReportStats', () => {
    it('should fetch report stats successfully', async () => {
      const mockReportStats = {
        total: 100,
        completed: 80,
        generating: 15,
        failed: 5
      }

      mockAxiosInstance.get.mockResolvedValue({
        data: mockReportStats
      })

      const result = await dashboardStatsService.getReportStats()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/report-stats/')
      expect(result).toEqual(mockReportStats)
    })
  })

  describe('dismissAlert', () => {
    it('should dismiss alert successfully', async () => {
      const alertId = 1
      const mockResponse = {
        success: true,
        message: 'Alert dismissed'
      }

      mockAxiosInstance.post.mockResolvedValue({
        data: mockResponse
      })

      const result = await dashboardStatsService.dismissAlert(alertId)

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/alerts/1/dismiss/')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getRealtimeMetrics', () => {
    it('should fetch realtime metrics successfully', async () => {
      const mockMetrics = {
        active_users: 50,
        requests_per_minute: 100,
        system_load: 0.75
      }

      mockAxiosInstance.get.mockResolvedValue({
        data: mockMetrics
      })

      const result = await dashboardStatsService.getRealtimeMetrics()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/realtime-metrics/')
      expect(result).toEqual(mockMetrics)
    })
  })

  describe('exportDashboardData', () => {
    it('should export dashboard data as JSON by default', async () => {
      const mockBlob = new Blob(['{"data": "test"}'], { type: 'application/json' })

      mockAxiosInstance.get.mockResolvedValue({
        data: mockBlob
      })

      const result = await dashboardStatsService.exportDashboardData()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith(
        '/export/?format=json&period=30',
        {
          responseType: 'blob'
        }
      )

      expect(result).toEqual(mockBlob)
    })

    it('should export dashboard data with custom format and period', async () => {
      const format = 'csv'
      const period = '7'
      const mockBlob = new Blob(['csv,data'], { type: 'text/csv' })

      mockAxiosInstance.get.mockResolvedValue({
        data: mockBlob
      })

      const result = await dashboardStatsService.exportDashboardData(format, period)

      expect(mockAxiosInstance.get).toHaveBeenCalledWith(
        '/export/?format=csv&period=7',
        {
          responseType: 'blob'
        }
      )

      expect(result).toEqual(mockBlob)
    })
  })

  describe('Request Interceptor', () => {
    it('should add authorization header from localStorage', () => {
      localStorageMock.getItem.mockReturnValue('test-token-123')

      const requestConfig = {
        headers: {}
      }

      const requestInterceptor = mockAxiosInstance.interceptors.request.use.mock.calls[0]?.[0]

      if (requestInterceptor) {
        const result = requestInterceptor(requestConfig)

        expect(localStorageMock.getItem).toHaveBeenCalled()
        expect(result.headers.Authorization).toBe('Bearer test-token-123')
      }
    })
  })

  describe('Response Interceptor', () => {
    it('should handle 401 error and redirect to login', () => {
      const error = {
        response: {
          status: 401
        }
      }

      const errorInterceptor = mockAxiosInstance.interceptors.response.use.mock.calls[0]?.[1]

      if (errorInterceptor) {
        errorInterceptor(error).catch(() => {})

        expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token')
      }
    })

    it('should not redirect on non-401 errors', () => {
      const error = {
        response: {
          status: 500
        }
      }

      const errorInterceptor = mockAxiosInstance.interceptors.response.use.mock.calls[0]?.[1]

      if (errorInterceptor) {
        const promise = errorInterceptor(error)

        expect(promise).rejects.toEqual(error)
      }
    })
  })
})


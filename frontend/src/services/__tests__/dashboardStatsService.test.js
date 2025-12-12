/**
 * Unit tests for DashboardStatsService
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import dashboardStatsService from '../dashboardStatsService.js'
import { apiGet, apiPost } from '../apiClient.js'

// Mock apiClient
vi.mock('../apiClient.js', () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn()
}))

describe('DashboardStatsService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getGeneralStats', () => {
    it('should get general stats', async () => {
      const mockStats = { totalUsers: 100, totalFincas: 50 }
      apiGet.mockResolvedValue(mockStats)
      
      const result = await dashboardStatsService.getGeneralStats()
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/stats/')
      expect(result).toEqual(mockStats)
    })
  })

  describe('getActivityData', () => {
    it('should get activity data with default period', async () => {
      const mockData = [{ date: '2024-01-01', count: 10 }]
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getActivityData()
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/activity/', { period: '30' })
      expect(result).toEqual(mockData)
    })

    it('should get activity data with custom period', async () => {
      const mockData = [{ date: '2024-01-01', count: 10 }]
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getActivityData('7')
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/activity/', { period: '7' })
      expect(result).toEqual(mockData)
    })
  })

  describe('getQualityDistribution', () => {
    it('should get quality distribution', async () => {
      const mockData = { excellent: 10, good: 20, fair: 15 }
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getQualityDistribution()
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/quality-distribution/')
      expect(result).toEqual(mockData)
    })
  })

  describe('getRegionStats', () => {
    it('should get region stats', async () => {
      const mockData = [{ region: 'Norte', count: 25 }]
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getRegionStats()
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/region-stats/')
      expect(result).toEqual(mockData)
    })
  })

  describe('getTrendsData', () => {
    it('should get trends data with default params', async () => {
      const mockData = [{ date: '2024-01-01', value: 85 }]
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getTrendsData()
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/trends/', { period: '30', metric: 'quality' })
      expect(result).toEqual(mockData)
    })

    it('should get trends data with custom params', async () => {
      const mockData = [{ date: '2024-01-01', value: 85 }]
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getTrendsData('7', 'production')
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/trends/', { period: '7', metric: 'production' })
      expect(result).toEqual(mockData)
    })
  })

  describe('getActiveUsers', () => {
    it('should get active users with default limit', async () => {
      const mockData = [{ id: 1, name: 'User 1', activity: 100 }]
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getActiveUsers()
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/active-users/', { limit: 10 })
      expect(result).toEqual(mockData)
    })

    it('should get active users with custom limit', async () => {
      const mockData = [{ id: 1, name: 'User 1' }]
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getActiveUsers(20)
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/active-users/', { limit: 20 })
      expect(result).toEqual(mockData)
    })
  })

  describe('getTopFincas', () => {
    it('should get top fincas', async () => {
      const mockData = [{ id: 1, name: 'Finca 1', quality: 95 }]
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getTopFincas()
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/top-fincas/', { limit: 10 })
      expect(result).toEqual(mockData)
    })
  })

  describe('getRecentUsers', () => {
    it('should get recent users', async () => {
      const mockData = [{ id: 1, name: 'New User', createdAt: '2024-01-01' }]
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getRecentUsers()
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/recent-users/', { limit: 10 })
      expect(result).toEqual(mockData)
    })
  })

  describe('getRecentActivities', () => {
    it('should get recent activities', async () => {
      const mockData = [{ id: 1, type: 'upload', timestamp: '2024-01-01' }]
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getRecentActivities()
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/recent-activities/', { limit: 10 })
      expect(result).toEqual(mockData)
    })
  })

  describe('getSystemAlerts', () => {
    it('should get system alerts', async () => {
      const mockData = [{ id: 1, message: 'Alert 1', level: 'warning' }]
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getSystemAlerts()
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/alerts/')
      expect(result).toEqual(mockData)
    })
  })

  describe('getReportStats', () => {
    it('should get report stats', async () => {
      const mockData = { total: 50, completed: 45, failed: 5 }
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getReportStats()
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/report-stats/')
      expect(result).toEqual(mockData)
    })
  })

  describe('dismissAlert', () => {
    it('should dismiss alert', async () => {
      const mockResponse = { success: true }
      apiPost.mockResolvedValue(mockResponse)
      
      const result = await dashboardStatsService.dismissAlert(1)
      
      expect(apiPost).toHaveBeenCalledWith('/api/dashboard/alerts/1/dismiss/')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getRealtimeMetrics', () => {
    it('should get realtime metrics', async () => {
      const mockData = { activeUsers: 10, processingJobs: 3 }
      apiGet.mockResolvedValue(mockData)
      
      const result = await dashboardStatsService.getRealtimeMetrics()
      
      expect(apiGet).toHaveBeenCalledWith('/api/dashboard/realtime-metrics/')
      expect(result).toEqual(mockData)
    })
  })

  describe('exportDashboardData', () => {
    it('should export dashboard data with default params', async () => {
      const mockBlob = new Blob(['data'])
      apiGet.mockResolvedValue(mockBlob)
      
      const result = await dashboardStatsService.exportDashboardData()
      
      expect(apiGet).toHaveBeenCalledWith(
        '/api/dashboard/export/',
        { format: 'json', period: '30' },
        { responseType: 'blob' }
      )
      expect(result).toEqual(mockBlob)
    })

    it('should export dashboard data with custom params', async () => {
      const mockBlob = new Blob(['data'])
      apiGet.mockResolvedValue(mockBlob)
      
      const result = await dashboardStatsService.exportDashboardData('csv', '7')
      
      expect(apiGet).toHaveBeenCalledWith(
        '/api/dashboard/export/',
        { format: 'csv', period: '7' },
        { responseType: 'blob' }
      )
      expect(result).toEqual(mockBlob)
    })
  })
})


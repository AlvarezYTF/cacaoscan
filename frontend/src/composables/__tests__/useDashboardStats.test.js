/**
 * Unit tests for useDashboardStats composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useDashboardStats } from '../useDashboardStats.js'
import dashboardStatsService from '@/services/dashboardStatsService'

// Mock dashboardStatsService
vi.mock('@/services/dashboardStatsService', () => ({
  default: {
    getGeneralStats: vi.fn(),
    getActivityData: vi.fn(),
    getQualityDistribution: vi.fn(),
    getRegionStats: vi.fn(),
    getTrendsData: vi.fn(),
    getActiveUsers: vi.fn(),
    getTopFincas: vi.fn(),
    getRecentUsers: vi.fn(),
    getRecentActivities: vi.fn(),
    getSystemAlerts: vi.fn(),
    getReportStats: vi.fn()
  }
}))

describe('useDashboardStats', () => {
  let stats

  beforeEach(() => {
    vi.clearAllMocks()
    stats = useDashboardStats()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(stats.loading.value).toBe(false)
      expect(stats.error.value).toBe(null)
      expect(stats.stats.value).toEqual({})
      expect(stats.activityData.value).toEqual({ labels: [], datasets: [] })
    })
  })

  describe('loadGeneralStats', () => {
    it('should load general stats successfully', async () => {
      const mockStats = {
        data: {
          total_users: 100,
          total_fincas: 50,
          total_analyses: 200
        }
      }
      dashboardStatsService.getGeneralStats.mockResolvedValue(mockStats)

      await stats.loadGeneralStats()

      expect(dashboardStatsService.getGeneralStats).toHaveBeenCalled()
      expect(stats.stats.value).toEqual(mockStats.data)
      expect(stats.loading.value).toBe(false)
    })

    it('should handle error', async () => {
      const error = new Error('Network error')
      dashboardStatsService.getGeneralStats.mockRejectedValue(error)

      await stats.loadGeneralStats()

      expect(stats.error.value).toBe('Network error')
      expect(stats.loading.value).toBe(false)
    })
  })

  describe('mainStats computed', () => {
    it('should compute main stats correctly', () => {
      stats.stats.value = {
        total_users: 100,
        total_fincas: 50,
        total_analyses: 200,
        avg_quality: 85
      }

      const mainStats = stats.mainStats.value

      expect(mainStats).toHaveLength(4)
      expect(mainStats[0].value).toBe(100)
      expect(mainStats[1].value).toBe(50)
      expect(mainStats[2].value).toBe(200)
      expect(mainStats[3].value).toBe(85)
    })

    it('should handle missing stats values', () => {
      stats.stats.value = {}

      const mainStats = stats.mainStats.value

      expect(mainStats[0].value).toBe(0)
      expect(mainStats[1].value).toBe(0)
      expect(mainStats[2].value).toBe(0)
      expect(mainStats[3].value).toBe(0)
    })

    it('should include change values in mainStats', () => {
      stats.stats.value = {
        total_users: 100,
        users_change: 5,
        total_fincas: 50,
        fincas_change: -2,
        total_analyses: 200,
        analyses_change: 10,
        avg_quality: 85,
        quality_change: 2
      }

      const mainStats = stats.mainStats.value

      expect(mainStats[0].change).toBe(5)
      expect(mainStats[1].change).toBe(-2)
      expect(mainStats[2].change).toBe(10)
      expect(mainStats[3].change).toBe(2)
    })

    it('should include trend data in mainStats', () => {
      stats.stats.value = {
        total_users: 100,
        users_trend: [1, 2, 3],
        total_fincas: 50,
        fincas_trend: [4, 5, 6]
      }

      const mainStats = stats.mainStats.value

      expect(mainStats[0].trend.data).toEqual([1, 2, 3])
      expect(mainStats[1].trend.data).toEqual([4, 5, 6])
    })
  })

  describe('loadActivityData', () => {
    it('should load activity data successfully', async () => {
      const mockResponse = {
        data: {
          labels: ['2024-01-01', '2024-01-02'],
          values: [10, 20]
        }
      }
      dashboardStatsService.getActivityData.mockResolvedValue(mockResponse)

      await stats.loadActivityData('30')

      expect(dashboardStatsService.getActivityData).toHaveBeenCalledWith('30')
      expect(stats.activityData.value.labels).toEqual(['2024-01-01', '2024-01-02'])
      expect(stats.activityData.value.datasets[0].data).toEqual([10, 20])
    })

    it('should handle loadActivityData error', async () => {
      const error = new Error('Network error')
      dashboardStatsService.getActivityData.mockRejectedValue(error)

      await stats.loadActivityData('30')

      expect(stats.activityData.value).toEqual({ labels: [], datasets: [] })
    })
  })

  describe('loadQualityData', () => {
    it('should load quality data successfully', async () => {
      const mockResponse = {
        data: {
          excelente: 10,
          buena: 20,
          regular: 15,
          baja: 5
        }
      }
      dashboardStatsService.getQualityDistribution.mockResolvedValue(mockResponse)

      await stats.loadQualityData()

      expect(stats.qualityData.value.labels).toEqual(['Excelente', 'Buena', 'Regular', 'Baja'])
      expect(stats.qualityData.value.datasets[0].data).toEqual([10, 20, 15, 5])
    })

    it('should handle missing quality data', async () => {
      const mockResponse = {
        data: {}
      }
      dashboardStatsService.getQualityDistribution.mockResolvedValue(mockResponse)

      await stats.loadQualityData()

      expect(stats.qualityData.value.datasets[0].data).toEqual([0, 0, 0, 0])
    })
  })

  describe('loadRegionData', () => {
    it('should load region data successfully', async () => {
      const mockResponse = {
        data: {
          labels: ['Cundinamarca', 'Antioquia'],
          values: [50, 30]
        }
      }
      dashboardStatsService.getRegionStats.mockResolvedValue(mockResponse)

      await stats.loadRegionData()

      expect(stats.regionData.value.labels).toEqual(['Cundinamarca', 'Antioquia'])
      expect(stats.regionData.value.datasets[0].data).toEqual([50, 30])
    })
  })

  describe('loadTrendsData', () => {
    it('should load trends data successfully', async () => {
      const mockResponse = {
        data: {
          labels: ['Jan', 'Feb', 'Mar'],
          values: [10, 20, 30]
        }
      }
      dashboardStatsService.getTrendsData.mockResolvedValue(mockResponse)

      await stats.loadTrendsData('30', 'quality')

      expect(dashboardStatsService.getTrendsData).toHaveBeenCalledWith('30', 'quality')
      expect(stats.trendsData.value.labels).toEqual(['Jan', 'Feb', 'Mar'])
      expect(stats.trendsData.value.datasets[0].data).toEqual([10, 20, 30])
    })
  })

  describe('loadActiveUsers', () => {
    it('should load active users successfully', async () => {
      const mockResponse = {
        data: [{ id: 1, username: 'user1' }]
      }
      dashboardStatsService.getActiveUsers.mockResolvedValue(mockResponse)

      await stats.loadActiveUsers(10)

      expect(dashboardStatsService.getActiveUsers).toHaveBeenCalledWith(10)
      expect(stats.activeUsers.value).toEqual([{ id: 1, username: 'user1' }])
    })
  })

  describe('loadTopFincas', () => {
    it('should load top fincas successfully', async () => {
      const mockResponse = {
        data: [{ id: 1, name: 'Finca 1' }]
      }
      dashboardStatsService.getTopFincas.mockResolvedValue(mockResponse)

      await stats.loadTopFincas(10)

      expect(dashboardStatsService.getTopFincas).toHaveBeenCalledWith(10)
      expect(stats.topFincas.value).toEqual([{ id: 1, name: 'Finca 1' }])
    })
  })

  describe('loadRecentUsers', () => {
    it('should load recent users successfully', async () => {
      const mockResponse = {
        data: [{ id: 1, username: 'user1' }]
      }
      dashboardStatsService.getRecentUsers.mockResolvedValue(mockResponse)

      await stats.loadRecentUsers(10)

      expect(stats.recentUsers.value).toEqual([{ id: 1, username: 'user1' }])
    })
  })

  describe('loadRecentActivities', () => {
    it('should load recent activities successfully', async () => {
      const mockResponse = {
        data: [{ id: 1, action: 'login' }]
      }
      dashboardStatsService.getRecentActivities.mockResolvedValue(mockResponse)

      await stats.loadRecentActivities(10)

      expect(stats.recentActivities.value).toEqual([{ id: 1, action: 'login' }])
    })
  })

  describe('loadSystemAlerts', () => {
    it('should load system alerts successfully', async () => {
      const mockResponse = {
        data: [{ id: 1, message: 'Alert' }]
      }
      dashboardStatsService.getSystemAlerts.mockResolvedValue(mockResponse)

      await stats.loadSystemAlerts()

      expect(stats.alerts.value).toEqual([{ id: 1, message: 'Alert' }])
    })
  })

  describe('loadReportStats', () => {
    it('should load report stats successfully', async () => {
      const mockResponse = {
        data: { total: 10, completed: 8 }
      }
      dashboardStatsService.getReportStats.mockResolvedValue(mockResponse)

      await stats.loadReportStats()

      expect(stats.reportStats.value).toEqual({ total: 10, completed: 8 })
    })
  })

  describe('loadAllData', () => {
    it('should load all data successfully', async () => {
      dashboardStatsService.getGeneralStats.mockResolvedValue({ data: {} })
      dashboardStatsService.getActivityData.mockResolvedValue({ data: { labels: [], values: [] } })
      dashboardStatsService.getQualityDistribution.mockResolvedValue({ data: {} })
      dashboardStatsService.getRegionStats.mockResolvedValue({ data: { labels: [], values: [] } })
      dashboardStatsService.getTrendsData.mockResolvedValue({ data: { labels: [], values: [] } })
      dashboardStatsService.getActiveUsers.mockResolvedValue({ data: [] })
      dashboardStatsService.getTopFincas.mockResolvedValue({ data: [] })
      dashboardStatsService.getRecentUsers.mockResolvedValue({ data: [] })
      dashboardStatsService.getRecentActivities.mockResolvedValue({ data: [] })
      dashboardStatsService.getSystemAlerts.mockResolvedValue({ data: [] })
      dashboardStatsService.getReportStats.mockResolvedValue({ data: {} })

      await stats.loadAllData('30')

      expect(stats.loading.value).toBe(false)
      expect(dashboardStatsService.getGeneralStats).toHaveBeenCalled()
    })

    it('should handle error in loadAllData', async () => {
      dashboardStatsService.getGeneralStats.mockRejectedValue(new Error('Error'))

      await stats.loadAllData('30')

      expect(stats.error.value).toBeTruthy()
      expect(stats.loading.value).toBe(false)
    })
  })

  describe('dismissAlert', () => {
    it('should dismiss alert successfully', async () => {
      stats.alerts.value = [
        { id: 1, message: 'Alert 1' },
        { id: 2, message: 'Alert 2' }
      ]
      dashboardStatsService.dismissAlert = vi.fn().mockResolvedValue({})

      await stats.dismissAlert(1)

      expect(dashboardStatsService.dismissAlert).toHaveBeenCalledWith(1)
      expect(stats.alerts.value).toHaveLength(1)
      expect(stats.alerts.value[0].id).toBe(2)
    })

    it('should handle dismissAlert error', async () => {
      dashboardStatsService.dismissAlert = vi.fn().mockRejectedValue(new Error('Error'))

      await expect(stats.dismissAlert(1)).rejects.toThrow()
    })
  })

  describe('exportData', () => {
    beforeEach(() => {
      globalThis.URL.createObjectURL = vi.fn(() => 'blob:url')
      globalThis.URL.revokeObjectURL = vi.fn()
      document.createElement = vi.fn(() => ({
        href: '',
        download: '',
        click: vi.fn(),
        remove: vi.fn()
      }))
      document.body.appendChild = vi.fn()
    })

    it('should export data successfully', async () => {
      const mockBlob = new Blob(['data'], { type: 'application/json' })
      dashboardStatsService.exportDashboardData = vi.fn().mockResolvedValue(mockBlob)

      await stats.exportData('json', '30')

      expect(dashboardStatsService.exportDashboardData).toHaveBeenCalledWith('json', '30')
    })
  })

  describe('refreshData', () => {
    it('should refresh all data', async () => {
      dashboardStatsService.getGeneralStats.mockResolvedValue({ data: {} })
      dashboardStatsService.getActivityData.mockResolvedValue({ data: { labels: [], values: [] } })
      dashboardStatsService.getQualityDistribution.mockResolvedValue({ data: {} })
      dashboardStatsService.getRegionStats.mockResolvedValue({ data: { labels: [], values: [] } })
      dashboardStatsService.getTrendsData.mockResolvedValue({ data: { labels: [], values: [] } })
      dashboardStatsService.getActiveUsers.mockResolvedValue({ data: [] })
      dashboardStatsService.getTopFincas.mockResolvedValue({ data: [] })
      dashboardStatsService.getRecentUsers.mockResolvedValue({ data: [] })
      dashboardStatsService.getRecentActivities.mockResolvedValue({ data: [] })
      dashboardStatsService.getSystemAlerts.mockResolvedValue({ data: [] })
      dashboardStatsService.getReportStats.mockResolvedValue({ data: {} })

      await stats.refreshData('30')

      expect(stats.loading.value).toBe(false)
    })
  })

  describe('transformToChartData', () => {
    it('should transform array data to chart format', () => {
      const rawData = [
        { label: 'A', value: 10 },
        { label: 'B', value: 20 }
      ]

      const result = stats.transformToChartData(rawData)

      expect(result.labels).toEqual(['A', 'B'])
      expect(result.datasets[0].data).toEqual([10, 20])
    })

    it('should use custom labelKey and valueKey', () => {
      const rawData = [
        { name: 'A', count: 10 },
        { name: 'B', count: 20 }
      ]

      const result = stats.transformToChartData(rawData, {
        labelKey: 'name',
        valueKey: 'count'
      })

      expect(result.labels).toEqual(['A', 'B'])
      expect(result.datasets[0].data).toEqual([10, 20])
    })

    it('should use provided labels and datasets', () => {
      const result = stats.transformToChartData([], {
        labels: ['A', 'B'],
        datasets: [{ data: [1, 2] }]
      })

      expect(result.labels).toEqual(['A', 'B'])
      expect(result.datasets[0].data).toEqual([1, 2])
    })
  })

  describe('aggregateByPeriod', () => {
    it('should aggregate data by day', () => {
      const data = [
        { date: '2024-01-01', value: 10 },
        { date: '2024-01-01', value: 20 },
        { date: '2024-01-02', value: 30 }
      ]

      const result = stats.aggregateByPeriod(data, 'day')

      expect(result.labels).toBeDefined()
      expect(result.datasets).toBeDefined()
    })

    it('should return empty for invalid data', () => {
      const result = stats.aggregateByPeriod([], 'day')
      expect(result).toEqual({ labels: [], datasets: [] })

      const result2 = stats.aggregateByPeriod(null, 'day')
      expect(result2).toEqual({ labels: [], datasets: [] })
    })
  })

  describe('filterByDateRange', () => {
    it('should filter chart data by date range', () => {
      const chartData = {
        labels: ['2024-01-01', '2024-01-15', '2024-02-01'],
        datasets: [{
          data: [10, 20, 30]
        }]
      }

      const startDate = new Date('2024-01-01')
      const endDate = new Date('2024-01-31')

      const result = stats.filterByDateRange(chartData, startDate, endDate)

      expect(result.labels.length).toBe(2)
    })
  })

  describe('getCacheKey', () => {
    it('should generate cache key', () => {
      const key = stats.getCacheKey('general', '30')
      expect(key).toBe('dashboard-stats-general-30')
    })
  })
})


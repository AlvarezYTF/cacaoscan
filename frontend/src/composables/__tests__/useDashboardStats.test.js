import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useDashboardStats } from '../useDashboardStats'
import dashboardStatsService from '@/services/dashboardStatsService'

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
    getReportStats: vi.fn(),
    dismissAlert: vi.fn(),
    exportDashboardData: vi.fn()
  }
}))

describe('useDashboardStats', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with default values', () => {
    const { loading, error, stats } = useDashboardStats()

    expect(loading.value).toBe(false)
    expect(error.value).toBe(null)
    expect(stats.value).toEqual({})
  })

  it('should load general stats', async () => {
    const mockStats = {
      total_users: 100,
      total_fincas: 50,
      total_analyses: 200,
      avg_quality: 85
    }

    dashboardStatsService.getGeneralStats.mockResolvedValue({
      data: mockStats
    })

    const { loadGeneralStats, stats, loading } = useDashboardStats()

    await loadGeneralStats()

    expect(dashboardStatsService.getGeneralStats).toHaveBeenCalled()
    expect(stats.value).toEqual(mockStats)
    expect(loading.value).toBe(false)
  })

  it('should handle error when loading general stats', async () => {
    const error = new Error('Network error')
    dashboardStatsService.getGeneralStats.mockRejectedValue(error)

    const { loadGeneralStats, error: errorRef, loading } = useDashboardStats()

    await loadGeneralStats()

    expect(errorRef.value).toBe('Network error')
    expect(loading.value).toBe(false)
  })

  it('should load activity data', async () => {
    const mockData = {
      labels: ['Jan', 'Feb', 'Mar'],
      values: [10, 20, 30]
    }

    dashboardStatsService.getActivityData.mockResolvedValue({
      data: mockData
    })

    const { loadActivityData, activityData } = useDashboardStats()

    await loadActivityData('30')

    expect(dashboardStatsService.getActivityData).toHaveBeenCalledWith('30')
    expect(activityData.value.labels).toEqual(mockData.labels)
    expect(activityData.value.datasets).toHaveLength(1)
  })

  it('should load quality data', async () => {
    const mockData = {
      excelente: 10,
      buena: 20,
      regular: 15,
      baja: 5
    }

    dashboardStatsService.getQualityDistribution.mockResolvedValue({
      data: mockData
    })

    const { loadQualityData, qualityData } = useDashboardStats()

    await loadQualityData()

    expect(qualityData.value.labels).toEqual(['Excelente', 'Buena', 'Regular', 'Baja'])
    expect(qualityData.value.datasets[0].data).toEqual([10, 20, 15, 5])
  })

  it('should load region data', async () => {
    const mockData = {
      labels: ['Region 1', 'Region 2'],
      values: [100, 200]
    }

    dashboardStatsService.getRegionStats.mockResolvedValue({
      data: mockData
    })

    const { loadRegionData, regionData } = useDashboardStats()

    await loadRegionData()

    expect(regionData.value.labels).toEqual(mockData.labels)
    expect(regionData.value.datasets[0].data).toEqual(mockData.values)
  })

  it('should load trends data', async () => {
    const mockData = {
      labels: ['Jan', 'Feb'],
      values: [50, 60]
    }

    dashboardStatsService.getTrendsData.mockResolvedValue({
      data: mockData
    })

    const { loadTrendsData, trendsData } = useDashboardStats()

    await loadTrendsData('30', 'quality')

    expect(dashboardStatsService.getTrendsData).toHaveBeenCalledWith('30', 'quality')
    expect(trendsData.value.labels).toEqual(mockData.labels)
  })

  it('should load active users', async () => {
    const mockUsers = [
      { id: 1, name: 'User 1' },
      { id: 2, name: 'User 2' }
    ]

    dashboardStatsService.getActiveUsers.mockResolvedValue({
      data: mockUsers
    })

    const { loadActiveUsers, activeUsers } = useDashboardStats()

    await loadActiveUsers(10)

    expect(dashboardStatsService.getActiveUsers).toHaveBeenCalledWith(10)
    expect(activeUsers.value).toEqual(mockUsers)
  })

  it('should load top fincas', async () => {
    const mockFincas = [
      { id: 1, nombre: 'Finca 1' },
      { id: 2, nombre: 'Finca 2' }
    ]

    dashboardStatsService.getTopFincas.mockResolvedValue({
      data: mockFincas
    })

    const { loadTopFincas, topFincas } = useDashboardStats()

    await loadTopFincas(10)

    expect(topFincas.value).toEqual(mockFincas)
  })

  it('should load recent users', async () => {
    const mockUsers = [{ id: 1, name: 'New User' }]

    dashboardStatsService.getRecentUsers.mockResolvedValue({
      data: mockUsers
    })

    const { loadRecentUsers, recentUsers } = useDashboardStats()

    await loadRecentUsers(10)

    expect(recentUsers.value).toEqual(mockUsers)
  })

  it('should load recent activities', async () => {
    const mockActivities = [{ id: 1, action: 'CREATE' }]

    dashboardStatsService.getRecentActivities.mockResolvedValue({
      data: mockActivities
    })

    const { loadRecentActivities, recentActivities } = useDashboardStats()

    await loadRecentActivities(10)

    expect(recentActivities.value).toEqual(mockActivities)
  })

  it('should load system alerts', async () => {
    const mockAlerts = [{ id: 1, message: 'Alert 1' }]

    dashboardStatsService.getSystemAlerts.mockResolvedValue({
      data: mockAlerts
    })

    const { loadSystemAlerts, alerts } = useDashboardStats()

    await loadSystemAlerts()

    expect(alerts.value).toEqual(mockAlerts)
  })

  it('should load report stats', async () => {
    const mockStats = { total: 10, completed: 8 }

    dashboardStatsService.getReportStats.mockResolvedValue({
      data: mockStats
    })

    const { loadReportStats, reportStats } = useDashboardStats()

    await loadReportStats()

    expect(reportStats.value).toEqual(mockStats)
  })

  it('should load all data', async () => {
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

    const { loadAllData, loading } = useDashboardStats()

    await loadAllData('30')

    expect(loading.value).toBe(false)
    expect(dashboardStatsService.getGeneralStats).toHaveBeenCalled()
  })

  it('should compute main stats', () => {
    const { stats, mainStats } = useDashboardStats()

    stats.value = {
      total_users: 100,
      total_fincas: 50,
      total_analyses: 200,
      avg_quality: 85
    }

    expect(mainStats.value).toHaveLength(4)
    expect(mainStats.value[0].value).toBe(100)
    expect(mainStats.value[1].value).toBe(50)
  })

  it('should dismiss alert', async () => {
    dashboardStatsService.dismissAlert.mockResolvedValue({})

    const { dismissAlert, alerts } = useDashboardStats()

    alerts.value = [
      { id: 1, message: 'Alert 1' },
      { id: 2, message: 'Alert 2' }
    ]

    await dismissAlert(1)

    expect(dashboardStatsService.dismissAlert).toHaveBeenCalledWith(1)
    expect(alerts.value).toHaveLength(1)
    expect(alerts.value[0].id).toBe(2)
  })

  it('should export data', async () => {
    // Mock URL.createObjectURL and URL.revokeObjectURL
    if (!globalThis.URL.createObjectURL) {
      globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
    }
    if (!globalThis.URL.revokeObjectURL) {
      globalThis.URL.revokeObjectURL = vi.fn()
    }
    const createObjectURLSpy = vi.spyOn(globalThis.URL, 'createObjectURL').mockReturnValue('blob:mock-url')
    const revokeObjectURLSpy = vi.spyOn(globalThis.URL, 'revokeObjectURL')

    const mockBlob = new Blob(['test'], { type: 'application/json' })
    dashboardStatsService.exportDashboardData.mockResolvedValue(mockBlob)

    const clickSpy = vi.fn()
    const removeSpy = vi.fn()

    // Create a real HTMLAnchorElement mock that extends HTMLElement
    const mockLink = document.createElement('a')
    mockLink.click = clickSpy
    mockLink.remove = removeSpy

    const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue(mockLink)
    const appendChildSpy = vi.spyOn(document.body, 'appendChild')

    const { exportData } = useDashboardStats()

    await exportData('json', '30')

    expect(dashboardStatsService.exportDashboardData).toHaveBeenCalledWith('json', '30')
    expect(createObjectURLSpy).toHaveBeenCalledWith(mockBlob)
    expect(mockLink.href).toBe('blob:mock-url')
    expect(mockLink.download).toBe('dashboard-data-30-days.json')
    expect(appendChildSpy).toHaveBeenCalledWith(mockLink)
    expect(clickSpy).toHaveBeenCalled()
    expect(removeSpy).toHaveBeenCalled()
    expect(revokeObjectURLSpy).toHaveBeenCalledWith('blob:mock-url')

    createElementSpy.mockRestore()
    appendChildSpy.mockRestore()
    removeSpy.mockRestore()
    createObjectURLSpy.mockRestore()
    revokeObjectURLSpy.mockRestore()
  })

  it('should refresh data', async () => {
    dashboardStatsService.getGeneralStats.mockResolvedValue({ data: {} })
    dashboardStatsService.getActivityData.mockResolvedValue({ data: { labels: [], values: [] } })
    dashboardStatsService.getQualityDistribution.mockResolvedValue({ data: {} })
    dashboardStatsService.getRegionStats.mockResolvedValue({ data: {} })
    dashboardStatsService.getTrendsData.mockResolvedValue({ data: {} })
    dashboardStatsService.getActiveUsers.mockResolvedValue({ data: [] })
    dashboardStatsService.getTopFincas.mockResolvedValue({ data: [] })
    dashboardStatsService.getRecentUsers.mockResolvedValue({ data: { results: [] } })
    dashboardStatsService.getRecentActivities.mockResolvedValue({ data: { results: [] } })
    dashboardStatsService.getSystemAlerts.mockResolvedValue({ data: { results: [] } })
    dashboardStatsService.getReportStats.mockResolvedValue({ data: {} })

    const { refreshData } = useDashboardStats()

    await refreshData('30')

    // refreshData calls loadAllData which calls multiple service methods
    expect(dashboardStatsService.getGeneralStats).toHaveBeenCalled()
    expect(dashboardStatsService.getActivityData).toHaveBeenCalledWith('30')
  })
})


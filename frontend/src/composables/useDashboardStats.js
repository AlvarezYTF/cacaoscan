/**
 * Composable para manejar estadísticas del dashboard
 */
import { ref, computed } from 'vue'
import dashboardStatsService from '@/services/dashboardStatsService'

export function useDashboardStats() {
  // Estado reactivo
  const loading = ref(false)
  const error = ref(null)
  const stats = ref({})
  const activityData = ref({ labels: [], datasets: [] })
  const qualityData = ref({ labels: [], datasets: [] })
  const regionData = ref({ labels: [], datasets: [] })
  const trendsData = ref({ labels: [], datasets: [] })
  const activeUsers = ref([])
  const topFincas = ref([])
  const recentUsers = ref([])
  const recentActivities = ref([])
  const alerts = ref([])
  const reportStats = ref({})

  // Estadísticas principales computadas
  const mainStats = computed(() => [
    {
      value: stats.value.total_users || 0,
      label: 'Usuarios Totales',
      icon: 'fas fa-users',
      change: stats.value.users_change || 0,
      changePeriod: 'vs mes anterior',
      variant: 'primary',
      trend: {
        data: stats.value.users_trend || [],
        color: '#3b82f6'
      }
    },
    {
      value: stats.value.total_fincas || 0,
      label: 'Fincas Registradas',
      icon: 'fas fa-seedling',
      change: stats.value.fincas_change || 0,
      changePeriod: 'vs mes anterior',
      variant: 'success',
      trend: {
        data: stats.value.fincas_trend || [],
        color: '#10b981'
      }
    },
    {
      value: stats.value.total_analyses || 0,
      label: 'Análisis Realizados',
      icon: 'fas fa-chart-line',
      change: stats.value.analyses_change || 0,
      changePeriod: 'vs mes anterior',
      variant: 'info',
      trend: {
        data: stats.value.analyses_trend || [],
        color: '#06b6d4'
      }
    },
    {
      value: stats.value.avg_quality || 0,
      label: 'Calidad Promedio',
      icon: 'fas fa-star',
      suffix: '%',
      change: stats.value.quality_change || 0,
      changePeriod: 'vs mes anterior',
      variant: 'warning',
      trend: {
        data: stats.value.quality_trend || [],
        color: '#f59e0b'
      }
    }
  ])

  // Métodos para cargar datos
  const loadGeneralStats = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await dashboardStatsService.getGeneralStats()
      stats.value = response.data
    } catch (err) {
      error.value = err.message
      } finally {
      loading.value = false
    }
  }

  const loadActivityData = async (period = '30') => {
    try {
      const response = await dashboardStatsService.getActivityData(period)
      activityData.value = {
        labels: response.data.labels,
        datasets: [{
          label: 'Actividad',
          data: response.data.values,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true
        }]
      }
    } catch (err) {
      }
  }

  const loadQualityData = async () => {
    try {
      const response = await dashboardStatsService.getQualityDistribution()
      qualityData.value = {
        labels: ['Excelente', 'Buena', 'Regular', 'Baja'],
        datasets: [{
          data: [
            response.data.excelente || 0,
            response.data.buena || 0,
            response.data.regular || 0,
            response.data.baja || 0
          ],
          backgroundColor: [
            '#10b981',
            '#3b82f6',
            '#f59e0b',
            '#ef4444'
          ]
        }]
      }
    } catch (err) {
      }
  }

  const loadRegionData = async () => {
    try {
      const response = await dashboardStatsService.getRegionStats()
      regionData.value = {
        labels: response.data.labels,
        datasets: [{
          label: 'Análisis por Región',
          data: response.data.values,
          backgroundColor: '#06b6d4'
        }]
      }
    } catch (err) {
      }
  }

  const loadTrendsData = async (period = '30', metric = 'quality') => {
    try {
      const response = await dashboardStatsService.getTrendsData(period, metric)
      trendsData.value = {
        labels: response.data.labels,
        datasets: [{
          label: metric.charAt(0).toUpperCase() + metric.slice(1),
          data: response.data.values,
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          fill: true
        }]
      }
    } catch (err) {
      }
  }

  const loadActiveUsers = async (limit = 10) => {
    try {
      const response = await dashboardStatsService.getActiveUsers(limit)
      activeUsers.value = response.data
    } catch (err) {
      }
  }

  const loadTopFincas = async (limit = 10) => {
    try {
      const response = await dashboardStatsService.getTopFincas(limit)
      topFincas.value = response.data
    } catch (err) {
      }
  }

  const loadRecentUsers = async (limit = 10) => {
    try {
      const response = await dashboardStatsService.getRecentUsers(limit)
      recentUsers.value = response.data
    } catch (err) {
      }
  }

  const loadRecentActivities = async (limit = 10) => {
    try {
      const response = await dashboardStatsService.getRecentActivities(limit)
      recentActivities.value = response.data
    } catch (err) {
      }
  }

  const loadSystemAlerts = async () => {
    try {
      const response = await dashboardStatsService.getSystemAlerts()
      alerts.value = response.data
    } catch (err) {
      }
  }

  const loadReportStats = async () => {
    try {
      const response = await dashboardStatsService.getReportStats()
      reportStats.value = response.data
    } catch (err) {
      }
  }

  // Método para cargar todos los datos
  const loadAllData = async (period = '30') => {
    loading.value = true
    error.value = null
    
    try {
      await Promise.all([
        loadGeneralStats(),
        loadActivityData(period),
        loadQualityData(),
        loadRegionData(),
        loadTrendsData(period),
        loadActiveUsers(),
        loadTopFincas(),
        loadRecentUsers(),
        loadRecentActivities(),
        loadSystemAlerts(),
        loadReportStats()
      ])
    } catch (err) {
      error.value = err.message
      } finally {
      loading.value = false
    }
  }

  // Métodos de utilidad
  const dismissAlert = async (alertId) => {
    try {
      await dashboardStatsService.dismissAlert(alertId)
      alerts.value = alerts.value.filter(alert => alert.id !== alertId)
    } catch (err) {
      throw err
    }
  }

  const exportData = async (format = 'json', period = '30') => {
    try {
      const blob = await dashboardStatsService.exportDashboardData(format, period)
      
      // Crear enlace de descarga
      const url = globalThis.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `dashboard-data-${period}-days.${format}`
      document.body.appendChild(link)
      link.click()
      link.remove()
      globalThis.URL.revokeObjectURL(url)
    } catch (err) {
      throw err
    }
  }

  const refreshData = async (period = '30') => {
    await loadAllData(period)
  }

  /**
   * Transform raw data to chart format
   * @param {Array} rawData - Raw data array
   * @param {Object} config - Transformation config
   * @returns {Object} Chart data object
   */
  const transformToChartData = (rawData, config = {}) => {
    const {
      labelKey = 'label',
      valueKey = 'value',
      labels = null,
      datasets = null,
      colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4']
    } = config

    if (labels && datasets) {
      return {
        labels,
        datasets: datasets.map((dataset, index) => ({
          ...dataset,
          backgroundColor: dataset.backgroundColor || colors[index % colors.length],
          borderColor: dataset.borderColor || colors[index % colors.length]
        }))
      }
    }

    if (Array.isArray(rawData)) {
      return {
        labels: rawData.map(item => item[labelKey] || item.name || item.label),
        datasets: [{
          label: config.datasetLabel || 'Datos',
          data: rawData.map(item => item[valueKey] || item.count || item.value),
          backgroundColor: colors[0],
          borderColor: colors[0]
        }]
      }
    }

    return { labels: [], datasets: [] }
  }

  /**
   * Aggregate data by time period
   * @param {Array} data - Data array with timestamps
   * @param {string} period - Time period (day, week, month)
   * @returns {Object} Aggregated chart data
   */
  const aggregateByPeriod = (data, period = 'day') => {
    if (!Array.isArray(data) || data.length === 0) {
      return { labels: [], datasets: [] }
    }

    const grouped = {}

    for (const item of data) {
      const date = new Date(item.date || item.timestamp || item.created_at)
      const key = formatDateKey(date, period)
      
      if (!grouped[key]) {
        grouped[key] = { count: 0, values: [] }
      }
      grouped[key].count++
      if (item.value !== undefined) {
        grouped[key].values.push(item.value)
      }
    }

    const labels = Object.keys(grouped).sort((a, b) => a.localeCompare(b))
    const values = labels.map(key => {
      const group = grouped[key]
      if (group.values.length > 0) {
        return group.values.reduce((a, b) => a + b, 0) / group.values.length
      }
      return group.count
    })

    return {
      labels,
      datasets: [{
        label: 'Datos',
        data: values,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true
      }]
    }
  }

  /**
   * Format date key for grouping
   * @param {Date} date - Date object
   * @param {string} period - Time period
   * @returns {string} Formatted key
   */
  const formatDateKey = (date, period) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')

    if (period === 'day') {
      return `${year}-${month}-${day}`
    } else if (period === 'week') {
      const week = getWeekNumber(date)
      return `${year}-W${String(week).padStart(2, '0')}`
    } else if (period === 'month') {
      return `${year}-${month}`
    }
    return `${year}-${month}-${day}`
  }

  /**
   * Get week number
   * @param {Date} date - Date object
   * @returns {number} Week number
   */
  const getWeekNumber = (date) => {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
    const dayNum = d.getUTCDay() || 7
    d.setUTCDate(d.getUTCDate() + 4 - dayNum)
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7)
  }

  /**
   * Filter chart data by date range
   * @param {Object} chartData - Chart data object
   * @param {Date} startDate - Start date
   * @param {Date} endDate - End date
   * @returns {Object} Filtered chart data
   */
  const filterByDateRange = (chartData, startDate, endDate) => {
    if (!chartData.labels || !chartData.datasets) {
      return chartData
    }

    const filteredLabels = []
    const filteredDatasets = chartData.datasets.map(dataset => ({
      ...dataset,
      data: []
    }))

    for (let index = 0; index < chartData.labels.length; index++) {
      const label = chartData.labels[index]
      const labelDate = new Date(label)
      if (labelDate >= startDate && labelDate <= endDate) {
        filteredLabels.push(label)
        for (let datasetIndex = 0; datasetIndex < chartData.datasets.length; datasetIndex++) {
          const dataset = chartData.datasets[datasetIndex]
          if (dataset.data[index] !== undefined) {
            filteredDatasets[datasetIndex].data.push(dataset.data[index])
          }
        }
      }
    }

    return {
      labels: filteredLabels,
      datasets: filteredDatasets
    }
  }

  /**
   * Cache key generator for stats
   * @param {string} type - Stats type
   * @param {string} period - Time period
   * @returns {string} Cache key
   */
  const getCacheKey = (type, period = '30') => {
    return `dashboard-stats-${type}-${period}`
  }

  return {
    // Estado
    loading,
    error,
    stats,
    activityData,
    qualityData,
    regionData,
    trendsData,
    activeUsers,
    topFincas,
    recentUsers,
    recentActivities,
    alerts,
    reportStats,
    
    // Computed
    mainStats,
    
    // Métodos
    loadGeneralStats,
    loadActivityData,
    loadQualityData,
    loadRegionData,
    loadTrendsData,
    loadActiveUsers,
    loadTopFincas,
    loadRecentUsers,
    loadRecentActivities,
    loadSystemAlerts,
    loadReportStats,
    loadAllData,
    dismissAlert,
    exportData,
    refreshData,
    
    // Chart data transformation methods
    transformToChartData,
    aggregateByPeriod,
    filterByDateRange,
    getCacheKey
  }
}

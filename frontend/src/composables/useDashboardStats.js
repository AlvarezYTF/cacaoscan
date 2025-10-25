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
      console.error('Error loading general stats:', err)
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
      console.error('Error loading activity data:', err)
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
      console.error('Error loading quality data:', err)
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
      console.error('Error loading region data:', err)
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
      console.error('Error loading trends data:', err)
    }
  }

  const loadActiveUsers = async (limit = 10) => {
    try {
      const response = await dashboardStatsService.getActiveUsers(limit)
      activeUsers.value = response.data
    } catch (err) {
      console.error('Error loading active users:', err)
    }
  }

  const loadTopFincas = async (limit = 10) => {
    try {
      const response = await dashboardStatsService.getTopFincas(limit)
      topFincas.value = response.data
    } catch (err) {
      console.error('Error loading top fincas:', err)
    }
  }

  const loadRecentUsers = async (limit = 10) => {
    try {
      const response = await dashboardStatsService.getRecentUsers(limit)
      recentUsers.value = response.data
    } catch (err) {
      console.error('Error loading recent users:', err)
    }
  }

  const loadRecentActivities = async (limit = 10) => {
    try {
      const response = await dashboardStatsService.getRecentActivities(limit)
      recentActivities.value = response.data
    } catch (err) {
      console.error('Error loading recent activities:', err)
    }
  }

  const loadSystemAlerts = async () => {
    try {
      const response = await dashboardStatsService.getSystemAlerts()
      alerts.value = response.data
    } catch (err) {
      console.error('Error loading system alerts:', err)
    }
  }

  const loadReportStats = async () => {
    try {
      const response = await dashboardStatsService.getReportStats()
      reportStats.value = response.data
    } catch (err) {
      console.error('Error loading report stats:', err)
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
      console.error('Error loading all dashboard data:', err)
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
      console.error('Error dismissing alert:', err)
      throw err
    }
  }

  const exportData = async (format = 'json', period = '30') => {
    try {
      const blob = await dashboardStatsService.exportDashboardData(format, period)
      
      // Crear enlace de descarga
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `dashboard-data-${period}-days.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Error exporting data:', err)
      throw err
    }
  }

  const refreshData = async (period = '30') => {
    await loadAllData(period)
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
    refreshData
  }
}

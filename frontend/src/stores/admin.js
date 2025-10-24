import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAdminStore = defineStore('admin', () => {
  // State
  const stats = ref({})
  const users = ref([])
  const activities = ref([])
  const reports = ref([])
  const alerts = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const totalUsers = computed(() => stats.value.total_users || 0)
  const totalFincas = computed(() => stats.value.total_fincas || 0)
  const totalAnalyses = computed(() => stats.value.total_analyses || 0)
  const avgQuality = computed(() => stats.value.avg_quality || 0)

  // Actions
  const getGeneralStats = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/admin/stats/')
      stats.value = response.data
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar estadísticas'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getRecentUsers = async (limit = 10) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get(`/admin/users/recent/?limit=${limit}`)
      users.value = response.data
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar usuarios recientes'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getRecentActivities = async (limit = 20) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get(`/audit/activity-logs/?limit=${limit}`)
      activities.value = response.data.results
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar actividades recientes'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getSystemAlerts = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/admin/alerts/')
      alerts.value = response.data
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar alertas'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getReportStats = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/reportes/stats/')
      reports.value = response.data
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar estadísticas de reportes'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getActivityData = async (period = '7') => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get(`/admin/activity-data/?period=${period}`)
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar datos de actividad'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getQualityDistribution = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/admin/quality-distribution/')
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar distribución de calidad'
      throw err
    } finally {
      loading.value = false
    }
  }

  const dismissAlert = async (alertId) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.post(`/admin/alerts/${alertId}/dismiss/`)
      
      // Remove alert from local state
      alerts.value = alerts.value.filter(alert => alert.id !== alertId)
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al descartar alerta'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getAllUsers = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/admin/users/', { params })
      users.value = response.data.results
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar usuarios'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getUserById = async (userId) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get(`/admin/users/${userId}/`)
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar usuario'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateUser = async (userId, userData) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.put(`/admin/users/${userId}/`, userData)
      
      // Update user in local state
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        users.value[index] = response.data
      }
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al actualizar usuario'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteUser = async (userId) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.delete(`/admin/users/${userId}/`)
      
      // Remove user from local state
      users.value = users.value.filter(user => user.id !== userId)
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al eliminar usuario'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getActivityLogs = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/audit/activity-logs/', { params })
      activities.value = response.data.results
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar logs de actividad'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getLoginHistory = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/audit/login-history/', { params })
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar historial de logins'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getAuditStats = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/audit/stats/')
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar estadísticas de auditoría'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getAllReports = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/reportes/', { params })
      reports.value = response.data.results
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar reportes'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createReport = async (reportData) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.post('/reportes/', reportData)
      
      // Add report to local state
      reports.value.unshift(response.data)
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al crear reporte'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteReport = async (reportId) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.delete(`/reportes/${reportId}/delete/`)
      
      // Remove report from local state
      reports.value = reports.value.filter(report => report.id !== reportId)
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al eliminar reporte'
      throw err
    } finally {
      loading.value = false
    }
  }

  const cleanupExpiredReports = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.post('/reportes/cleanup/')
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al limpiar reportes expirados'
      throw err
    } finally {
      loading.value = false
    }
  }

  const exportData = async (type, format = 'excel', params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get(`/admin/export/${type}/`, {
        params: { ...params, format },
        responseType: 'blob'
      })
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al exportar datos'
      throw err
    } finally {
      loading.value = false
    }
  }

  const sendNotification = async (notificationData) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.post('/notifications/create/', notificationData)
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al enviar notificación'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getSystemHealth = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/admin/system-health/')
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al verificar salud del sistema'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const resetState = () => {
    stats.value = {}
    users.value = []
    activities.value = []
    reports.value = []
    alerts.value = []
    loading.value = false
    error.value = null
  }

  return {
    // State
    stats,
    users,
    activities,
    reports,
    alerts,
    loading,
    error,
    
    // Getters
    totalUsers,
    totalFincas,
    totalAnalyses,
    avgQuality,
    
    // Actions
    getGeneralStats,
    getRecentUsers,
    getRecentActivities,
    getSystemAlerts,
    getReportStats,
    getActivityData,
    getQualityDistribution,
    dismissAlert,
    getAllUsers,
    getUserById,
    updateUser,
    deleteUser,
    getActivityLogs,
    getLoginHistory,
    getAuditStats,
    getAllReports,
    createReport,
    deleteReport,
    cleanupExpiredReports,
    exportData,
    sendNotification,
    getSystemHealth,
    clearError,
    resetState
  }
})

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { handleApiError } from '@/services/apiErrorHandler'

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
      
      const response = await api.get('/auth/admin/stats/')
      console.log('🔍 [admin store] Respuesta completa:', response)
      console.log('📊 [admin store] response.data:', response.data)
      stats.value = response.data
      console.log('✅ [admin store] stats.value actualizado:', stats.value)
      
      return response
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const getRecentUsers = async (limit = 10) => {
    try {
      loading.value = true
      error.value = null
      
      // Usar el endpoint de usuarios con limit
      const response = await api.get('/auth/users/', { 
        params: { 
          page_size: limit, 
          ordering: '-date_joined' 
        } 
      })
      users.value = response.data.results || response.data
      
      return response
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const getRecentActivities = async (limit = 20) => {
    try {
      loading.value = true
      error.value = null
      
      // El backend usa page_size, no limit
      const response = await api.get('/audit/activity-logs/', {
        params: {
          page_size: limit,
          page: 1,
          ordering: '-timestamp' // Ordenar por más reciente primero
        }
      })
      
      activities.value = response.data.results || []
      console.log('📊 [admin store] Activities response:', response.data)
      console.log('📊 [admin store] Activities count:', activities.value.length)
      
      return response
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: false })
      
      // Si es error 500 o el endpoint no está disponible, retornar vacío silenciosamente
      if (err.response?.status === 500) {
        console.warn('⚠️ [admin store] Activity logs endpoint returned 500, returning empty array')
        activities.value = []
        return { data: { results: [] } }
      }
      
      error.value = errorInfo.message
      // No lanzar el error para evitar notificaciones molestas
      activities.value = []
      return { data: { results: [] } }
    } finally {
      loading.value = false
    }
  }

  const getSystemAlerts = async () => {
    try {
      loading.value = true
      error.value = null
      
      // Las alertas se manejan a través de notificaciones
      // Obtener solo las no leídas y limitar a 10
      const response = await api.get('/notifications/', {
        params: {
          leida: false,
          page_size: 10,
          page: 1,
          ordering: '-fecha_creacion'
        }
      })
      
      const data = response.data || {}
      const notificationsArray = data.results || data.data || (Array.isArray(data) ? data : [])
      
      console.log('🚨 [admin store] Notifications response:', data)
      console.log('🚨 [admin store] Notifications count:', notificationsArray.length)
      
      alerts.value = notificationsArray
      
      return response
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: false })
      
      // Si es error 500 o el endpoint no está disponible, retornar vacío silenciosamente
      if (err.response?.status === 500) {
        console.warn('⚠️ [admin store] Notifications endpoint returned 500, returning empty array')
        alerts.value = []
        return { data: { results: [] } }
      }
      
      error.value = errorInfo.message
      // No lanzar el error para evitar notificaciones molestas
      alerts.value = []
      return { data: { results: [] } }
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
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const getActivityData = async (period = '7') => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/audit/activity-logs/')
      
      return response
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: false })
      
      // Si es error 500 o el endpoint no está disponible, retornar vacío silenciosamente
      if (err.response?.status === 500) {
        return { data: { results: [] } }
      }
      
      error.value = errorInfo.message
      // No lanzar el error para evitar notificaciones molestas
      return { data: { results: [] } }
    } finally {
      loading.value = false
    }
  }

  const getQualityDistribution = async () => {
    try {
      loading.value = true
      error.value = null
      
      // Usar endpoint de imágenes stats
      const response = await api.get('/images/stats/')
      
      return response
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const dismissAlert = async (alertId) => {
    try {
      loading.value = true
      error.value = null
      
      // Usar el endpoint correcto del backend
      const response = await api.post(`/notifications/${alertId}/read/`)
      
      // Remove alert from local state
      alerts.value = alerts.value.filter(alert => alert.id !== alertId)
      
      console.log('✅ [admin store] Alert dismissed:', alertId)
      
      return response
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const getAllUsers = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/auth/users/', { params })
      users.value = response.data.results || response.data
      
      return response
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const getUserById = async (userId) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get(`/auth/users/${userId}/`)
      
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
      
      const response = await api.patch(`/auth/users/${userId}/update/`, userData)
      
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
      
      const response = await api.delete(`/auth/users/${userId}/delete/`)
      
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
      
      // Usar endpoint de export de imágenes si existe, sino devolver error
      const endpoint = type === 'images' ? '/images/export/' : null
      
      if (!endpoint) {
        throw new Error(`Exportación de tipo ${type} no disponible`)
      }
      
      const response = await api.get(endpoint, {
        params: { ...params, format },
        responseType: 'blob'
      })
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Error al exportar datos'
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
      
      // Usar endpoint de stats generales como health check
      const response = await api.get('/auth/admin/stats/')
      
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

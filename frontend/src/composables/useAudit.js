/**
 * Composable for audit management
 * Consolidates audit operations, filtering, formatting, and reporting
 */
import { ref, reactive, computed } from 'vue'
import { useNotificationStore } from '@/stores/notifications'
import { useDateFormatting } from './useDateFormatting'
import * as auditApi from '@/services/auditApi'
import { useAuditHelpers } from './useAuditHelpers'

/**
 * Main useAudit composable
 * @param {Object} options - Configuration options
 * @returns {Object} Audit composable methods and state
 */
export function useAudit(options = {}) {
  const notificationStore = useNotificationStore()
  const { formatDate, formatDateTime } = useDateFormatting()
  const auditHelpers = useAuditHelpers()
  
  // State
  const loading = ref(false)
  const error = ref(null)
  const activityLogs = ref([])
  const loginHistory = ref([])
  const stats = ref(null)
  
  // Filters
  const activityFilters = reactive({
    usuario: '',
    accion: '',
    fecha_desde: '',
    fecha_hasta: '',
    page: 1,
    page_size: 50
  })
  
  const loginFilters = reactive({
    usuario: '',
    exitoso: null,
    fecha_desde: '',
    fecha_hasta: '',
    page: 1,
    page_size: 50
  })
  
  // Pagination
  const activityPagination = ref({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    itemsPerPage: 50
  })
  
  const loginPagination = ref({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    itemsPerPage: 50
  })
  
  // Computed
  const hasActivityFilters = computed(() => {
    return !!(
      activityFilters.usuario ||
      activityFilters.accion ||
      activityFilters.fecha_desde ||
      activityFilters.fecha_hasta
    )
  })
  
  const hasLoginFilters = computed(() => {
    return !!(
      loginFilters.usuario ||
      loginFilters.exitoso !== null ||
      loginFilters.fecha_desde ||
      loginFilters.fecha_hasta
    )
  })
  
  /**
   * Load activity logs
   * @param {Object} params - Filter and pagination parameters
   * @returns {Promise<Array>} List of activity logs
   */
  const loadActivityLogs = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const filters = { ...activityFilters, ...params }
      
      // Validate date filters
      const validation = auditApi.validateDateFilters(filters)
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '))
      }
      
      const result = await auditApi.getActivityLogs(filters)
      
      if (!result.success) {
        throw new Error(result.error)
      }
      
      const data = result.data
      
      // Format logs
      activityLogs.value = (data.results || []).map(log => auditApi.formatActivityLog(log))
      
      // Update pagination
      activityPagination.value = {
        currentPage: data.current_page || filters.page || 1,
        totalPages: data.total_pages || Math.ceil((data.count || 0) / (filters.page_size || 50)),
        totalItems: data.count || 0,
        itemsPerPage: filters.page_size || 50
      }
      
      return activityLogs.value
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar los logs de actividad'
      error.value = errorMessage
      
      notificationStore.addNotification({
        type: 'error',
        title: 'Error',
        message: errorMessage
      })
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Load login history
   * @param {Object} params - Filter and pagination parameters
   * @returns {Promise<Array>} List of login history records
   */
  const loadLoginHistory = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const filters = { ...loginFilters, ...params }
      
      // Validate date filters
      const validation = auditApi.validateDateFilters(filters)
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '))
      }
      
      const result = await auditApi.getLoginHistory(filters)
      
      if (!result.success) {
        throw new Error(result.error)
      }
      
      const data = result.data
      
      // Format login history
      loginHistory.value = (data.results || []).map(login => auditApi.formatLoginHistory(login))
      
      // Update pagination
      loginPagination.value = {
        currentPage: data.current_page || filters.page || 1,
        totalPages: data.total_pages || Math.ceil((data.count || 0) / (filters.page_size || 50)),
        totalItems: data.count || 0,
        itemsPerPage: filters.page_size || 50
      }
      
      return loginHistory.value
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar el historial de logins'
      error.value = errorMessage
      
      notificationStore.addNotification({
        type: 'error',
        title: 'Error',
        message: errorMessage
      })
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Load audit statistics
   * @param {Object} params - Filter parameters
   * @returns {Promise<Object>} Audit statistics
   */
  const loadStats = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await auditApi.getAuditStats(params)
      
      if (!result.success) {
        throw new Error(result.error)
      }
      
      stats.value = result.data
      
      return stats.value
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar las estadísticas de auditoría'
      error.value = errorMessage
      
      notificationStore.addNotification({
        type: 'error',
        title: 'Error',
        message: errorMessage
      })
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Generate audit report
   * @param {Object} reportParams - Report parameters
   * @returns {Promise<Object>} Report generation result
   */
  const generateReport = async (reportParams) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await auditApi.generateAuditReport(reportParams)
      
      if (!result.success) {
        throw new Error(result.error)
      }
      
      notificationStore.addNotification({
        type: 'success',
        title: 'Reporte generado',
        message: 'El reporte de auditoría se ha generado exitosamente'
      })
      
      return result.data
    } catch (err) {
      const errorMessage = err.message || 'Error al generar el reporte'
      error.value = errorMessage
      
      notificationStore.addNotification({
        type: 'error',
        title: 'Error',
        message: errorMessage
      })
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Get user activity summary
   * @param {number} userId - User ID
   * @param {Object} params - Additional parameters
   * @returns {Promise<Object>} User activity summary
   */
  const getUserActivitySummary = async (userId, params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await auditApi.getUserActivitySummary(userId, params)
      
      if (!result.success) {
        throw new Error(result.error)
      }
      
      return result.data
    } catch (err) {
      const errorMessage = err.message || 'Error al obtener el resumen de actividad'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Apply activity filters
   * @param {Object} newFilters - New filter values
   */
  const applyActivityFilters = (newFilters) => {
    Object.assign(activityFilters, newFilters)
    activityFilters.page = 1 // Reset to first page
  }
  
  /**
   * Clear activity filters
   */
  const clearActivityFilters = () => {
    Object.assign(activityFilters, {
      usuario: '',
      accion: '',
      fecha_desde: '',
      fecha_hasta: '',
      page: 1
    })
  }
  
  /**
   * Apply login filters
   * @param {Object} newFilters - New filter values
   */
  const applyLoginFilters = (newFilters) => {
    Object.assign(loginFilters, newFilters)
    loginFilters.page = 1 // Reset to first page
  }
  
  /**
   * Clear login filters
   */
  const clearLoginFilters = () => {
    Object.assign(loginFilters, {
      usuario: '',
      exitoso: null,
      fecha_desde: '',
      fecha_hasta: '',
      page: 1
    })
  }
  
  /**
   * Format action type label
   * @param {string} action - Action type
   * @returns {string} Formatted label
   */
  const formatActionType = (action) => {
    const actionLabels = {
      'login': 'Inicio de sesión',
      'logout': 'Cierre de sesión',
      'create': 'Crear',
      'update': 'Actualizar',
      'delete': 'Eliminar',
      'view': 'Ver',
      'download': 'Descargar',
      'upload': 'Subir',
      'export': 'Exportar',
      'import': 'Importar',
      'train': 'Entrenar',
      'predict': 'Predecir'
    }
    return actionLabels[action] || action
  }
  
  /**
   * Get action icon
   * @param {string} action - Action type
   * @returns {string} Icon class
   */
  const getActionIcon = (action) => {
    const icon = auditApi.AUDIT_CONFIG.ACTION_ICONS[action] || 'info-circle'
    return `fas fa-${icon}`
  }
  
  /**
   * Get action color
   * @param {string} action - Action type
   * @returns {string} Color class
   */
  const getActionColor = (action) => {
    const color = auditApi.AUDIT_CONFIG.ACTION_COLORS[action] || 'gray'
    return `text-${color}`
  }
  
  /**
   * Clear error state
   */
  const clearError = () => {
    error.value = null
  }
  
  return {
    // State
    loading,
    error,
    activityLogs,
    loginHistory,
    stats,
    activityFilters,
    loginFilters,
    activityPagination,
    loginPagination,
    
    // Computed
    hasActivityFilters,
    hasLoginFilters,
    
    // Methods
    loadActivityLogs,
    loadLoginHistory,
    loadStats,
    generateReport,
    getUserActivitySummary,
    applyActivityFilters,
    clearActivityFilters,
    applyLoginFilters,
    clearLoginFilters,
    formatActionType,
    getActionIcon,
    getActionColor,
    clearError,
    
    // Utilities
    formatDate,
    formatDateTime,
    
    // Helpers (re-exported from useAuditHelpers)
    ...auditHelpers,
    
    // Constants (re-exported from auditApi)
    AUDIT_ACTION_TYPES: auditApi.AUDIT_ACTION_TYPES,
    AUDIT_SEVERITY_LEVELS: auditApi.AUDIT_SEVERITY_LEVELS,
    AUDIT_CONFIG: auditApi.AUDIT_CONFIG
  }
}


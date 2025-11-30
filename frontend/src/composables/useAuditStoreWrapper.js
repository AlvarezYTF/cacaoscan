/**
 * Composable wrapper for audit store with domain-specific helpers
 */
import { computed } from 'vue'
import { useAuditStore } from '@/stores/audit'

/**
 * Provides audit store wrapper with formatting utilities
 * @returns {Object} Audit store wrapper with helpers
 */
export function useAuditStoreWrapper() {
  const store = useAuditStore()

  /**
   * Fetches audit logs with filters
   * @param {Object} filters - Filter parameters
   * @param {string} filters.user - Username filter
   * @param {string} filters.action - Action filter
   * @param {string} filters.model - Model filter
   * @param {string} filters.startDate - Start date filter
   * @param {string} filters.endDate - End date filter
   * @param {number} filters.page - Page number
   * @param {number} filters.pageSize - Page size
   * @returns {Promise<void>}
   */
  const fetchAuditLogs = async (filters = {}) => {
    const params = {}
    
    if (filters.user) params.usuario = filters.user
    if (filters.action) params.accion = filters.action
    if (filters.model) params.modelo = filters.model
    if (filters.startDate) params.fecha_inicio = filters.startDate
    if (filters.endDate) params.fecha_fin = filters.endDate
    if (filters.page) params.page = filters.page
    if (filters.pageSize) params.page_size = filters.pageSize

    await store.fetchActivityLogs(params)
  }

  /**
   * Exports audit logs with filters
   * @param {Object} filters - Filter parameters
   * @param {string} filters.format - Export format (json, csv, xlsx)
   * @returns {Promise<void>}
   */
  const exportAuditLogs = async (filters = {}) => {
    const params = { format: filters.format || 'json' }
    
    if (filters.user) params.usuario = filters.user
    if (filters.action) params.accion = filters.action
    if (filters.model) params.modelo = filters.model
    if (filters.startDate) params.fecha_inicio = filters.startDate
    if (filters.endDate) params.fecha_fin = filters.endDate

    await store.exportActivityLogs(params)
  }

  /**
   * Formats audit action for display
   * @param {string} action - Action name
   * @returns {string} Formatted action name
   */
  const formatAuditAction = (action) => {
    const actionMap = {
      'create': 'Crear',
      'update': 'Actualizar',
      'delete': 'Eliminar',
      'view': 'Ver',
      'login': 'Inicio de sesión',
      'logout': 'Cierre de sesión',
      'export': 'Exportar',
      'import': 'Importar'
    }
    return actionMap[action] || action
  }

  /**
   * Formats audit date for display
   * @param {string} dateString - Date string
   * @returns {string} Formatted date
   */
  const formatAuditDate = (dateString) => {
    if (!dateString) return ''
    
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) {
      return 'Hace un momento'
    } else if (diffMins < 60) {
      return `Hace ${diffMins} ${diffMins === 1 ? 'minuto' : 'minutos'}`
    } else if (diffHours < 24) {
      return `Hace ${diffHours} ${diffHours === 1 ? 'hora' : 'horas'}`
    } else if (diffDays < 7) {
      return `Hace ${diffDays} ${diffDays === 1 ? 'día' : 'días'}`
    } else {
      return date.toLocaleDateString('es-CO', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }

  /**
   * Gets action type category
   * @param {string} action - Action name
   * @returns {string} Action category (create, update, delete, view, auth, other)
   */
  const getActionCategory = (action) => {
    const createActions = ['create', 'add', 'new']
    const updateActions = ['update', 'edit', 'modify', 'change']
    const deleteActions = ['delete', 'remove', 'destroy']
    const viewActions = ['view', 'read', 'get', 'list']
    const authActions = ['login', 'logout', 'register', 'password_reset']

    const lowerAction = action.toLowerCase()

    if (createActions.some(a => lowerAction.includes(a))) return 'create'
    if (updateActions.some(a => lowerAction.includes(a))) return 'update'
    if (deleteActions.some(a => lowerAction.includes(a))) return 'delete'
    if (viewActions.some(a => lowerAction.includes(a))) return 'view'
    if (authActions.some(a => lowerAction.includes(a))) return 'auth'

    return 'other'
  }

  /**
   * Gets action color for UI
   * @param {string} action - Action name
   * @returns {string} Color class
   */
  const getActionColor = (action) => {
    const category = getActionCategory(action)
    const colorMap = {
      create: 'text-green-600 bg-green-50',
      update: 'text-blue-600 bg-blue-50',
      delete: 'text-red-600 bg-red-50',
      view: 'text-gray-600 bg-gray-50',
      auth: 'text-purple-600 bg-purple-50',
      other: 'text-yellow-600 bg-yellow-50'
    }
    return colorMap[category] || colorMap.other
  }

  return {
    // Store state (computed for reactivity)
    logs: computed(() => store.activityLogs),
    loginHistory: computed(() => store.loginHistory),
    stats: computed(() => store.stats),
    pagination: computed(() => store.pagination),
    loading: computed(() => store.loading),
    error: computed(() => store.error),

    // Helper methods
    fetchAuditLogs,
    exportAuditLogs,
    formatAuditAction,
    formatAuditDate,
    getActionCategory,
    getActionColor,

    // Store methods (for advanced usage)
    store
  }
}


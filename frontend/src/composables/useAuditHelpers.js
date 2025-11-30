/**
 * Composable for audit-related helper functions
 * Provides reusable audit formatting and utility functions
 */

/**
 * Get audit action icon class
 * @param {string} action - Action type
 * @returns {string} Icon class name
 */
export function getAuditActionIcon(action) {
  const actionIcons = {
    'login': 'fas fa-sign-in-alt',
    'logout': 'fas fa-sign-out-alt',
    'create': 'fas fa-plus',
    'update': 'fas fa-edit',
    'delete': 'fas fa-trash',
    'view': 'fas fa-eye',
    'download': 'fas fa-download',
    'upload': 'fas fa-upload',
    'analysis': 'fas fa-chart-line',
    'training': 'fas fa-brain',
    'report': 'fas fa-file-alt',
    'error': 'fas fa-exclamation-triangle'
  }
  return actionIcons[action] || 'fas fa-circle'
}

/**
 * Get audit action marker class
 * @param {string} action - Action type
 * @returns {string} Marker class name
 */
export function getAuditActionMarkerClass(action) {
  const actionClasses = {
    'login': 'marker-login',
    'logout': 'marker-logout',
    'create': 'marker-create',
    'update': 'marker-update',
    'delete': 'marker-delete',
    'view': 'marker-view',
    'download': 'marker-download',
    'upload': 'marker-upload',
    'analysis': 'marker-analysis',
    'training': 'marker-training',
    'report': 'marker-report',
    'error': 'marker-error'
  }
  return actionClasses[action] || 'marker-default'
}

/**
 * Get audit item title based on audit type
 * @param {Object} item - Audit item
 * @param {string} auditType - Type of audit ('activity', 'login', 'both')
 * @returns {string} Item title
 */
export function getAuditItemTitle(item, auditType) {
  if (auditType === 'activity' || auditType === 'both') {
    return `${item.accion_display || item.accion} - ${item.modelo}`
  } else if (auditType === 'login') {
    return `Login ${item.success ? 'Exitoso' : 'Fallido'}`
  }
  return 'Evento de Auditoría'
}

/**
 * Get audit item type label
 * @param {string} auditType - Type of audit ('activity', 'login', 'both')
 * @returns {string} Type label
 */
export function getAuditItemType(auditType) {
  if (auditType === 'activity' || auditType === 'both') {
    return 'Actividad'
  } else if (auditType === 'login') {
    return 'Login'
  }
  return 'Evento'
}

/**
 * Get audit item status
 * @param {Object} item - Audit item
 * @param {string} auditType - Type of audit ('activity', 'login', 'both')
 * @returns {string} Status text
 */
export function getAuditItemStatus(item, auditType) {
  if (auditType === 'activity' || auditType === 'both') {
    return item.accion_display || item.accion
  } else if (auditType === 'login') {
    return item.success ? 'Exitoso' : 'Fallido'
  }
  return 'Completado'
}

/**
 * Get audit status CSS class
 * @param {Object} item - Audit item
 * @param {string} auditType - Type of audit ('activity', 'login', 'both')
 * @returns {string} CSS class name
 */
export function getAuditStatusClass(item, auditType) {
  if (auditType === 'login' || auditType === 'both') {
    return item.success ? 'status-success' : 'status-error'
  }
  return 'status-default'
}

/**
 * Format JSON data for display
 * @param {Object|string} data - Data to format
 * @returns {string} Formatted JSON string
 */
export function formatJson(data) {
  // Handle null and undefined first
  if (data === null) return 'null'
  if (data === undefined) return 'undefined'
  
  // Try to format as JSON
  try {
    const parsed = typeof data === 'string' ? JSON.parse(data) : data
    if (typeof parsed === 'object' && parsed !== null) {
      return JSON.stringify(parsed, null, 2)
    }
    return String(parsed)
  } catch {
    // Fallback: convert primitive types to string
    const type = typeof data
    if (type === 'object' && data !== null) {
      try {
        return JSON.stringify(data, null, 2)
      } catch {
        return '[Object]'
      }
    }
    
    // Only stringify primitive types that are safe
    if (type === 'string') {
      return data
    }
    if (type === 'number') {
      return data.toString()
    }
    if (type === 'boolean') {
      return data.toString()
    }
    // For other types (symbol, function, etc.), return a safe representation
    return '[Unknown]'
  }
}

/**
 * Composable function that returns all audit helper utilities
 * @returns {Object} Object with all audit helper functions
 */
export function useAuditHelpers() {
  return {
    getAuditActionIcon,
    getAuditActionMarkerClass,
    getAuditItemTitle,
    getAuditItemType,
    getAuditItemStatus,
    getAuditStatusClass,
    formatJson
  }
}


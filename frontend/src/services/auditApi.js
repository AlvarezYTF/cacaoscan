/**
 * Servicio API para sistema de auditoría
 * 
 * Maneja todas las operaciones relacionadas con el sistema de auditoría:
 * - Logs de actividad
 * - Historial de login
 * - Estadísticas de auditoría
 * 
 * Solo accesible para usuarios con rol de administrador
 */

import { apiGet } from './apiClient'

// Endpoints de la API
const API_ENDPOINTS = {
  activityLogs: '/audit/activity-logs/',
  loginHistory: '/audit/login-history/',
  stats: '/audit/stats/'
}

/**
 * Obtiene lista de logs de actividad
 * @param {Object} params - Parámetros de consulta
 * @param {number} params.page - Página actual
 * @param {number} params.page_size - Tamaño de página
 * @param {string} params.usuario - Filtrar por usuario
 * @param {string} params.accion - Filtrar por tipo de acción
 * @param {string} params.fecha_desde - Fecha inicio (YYYY-MM-DD)
 * @param {string} params.fecha_hasta - Fecha fin (YYYY-MM-DD)
 * @returns {Promise<Object>} - Lista paginada de logs normalizada
 */
export async function getActivityLogs(params = {}) {
  try {
    const data = await apiGet(API_ENDPOINTS.activityLogs, params)
    
    // Normalize response
    return {
      success: true,
      data: {
        results: data.results || [],
        count: data.count || 0,
        current_page: data.current_page || params.page || 1,
        total_pages: data.total_pages || Math.ceil((data.count || 0) / (params.page_size || 50)),
        page_size: data.page_size || params.page_size || 50
      }
    }
  } catch (error) {
    console.error('Error obteniendo logs de actividad:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener los logs de actividad'

    throw new Error(errorMessage)
  }
}

/**
 * Obtiene historial de login de usuarios
 * @param {Object} params - Parámetros de consulta
 * @param {number} params.page - Página actual
 * @param {number} params.page_size - Tamaño de página
 * @param {string} params.usuario - Filtrar por usuario
 * @param {boolean} params.exitoso - Filtrar por logins exitosos/fallidos
 * @param {string} params.fecha_desde - Fecha inicio (YYYY-MM-DD)
 * @param {string} params.fecha_hasta - Fecha fin (YYYY-MM-DD)
 * @returns {Promise<Object>} - Lista paginada de logins normalizada
 */
export async function getLoginHistory(params = {}) {
  try {
    const data = await apiGet(API_ENDPOINTS.loginHistory, params)
    
    // Normalize response
    return {
      success: true,
      data: {
        results: data.results || [],
        count: data.count || 0,
        current_page: data.current_page || params.page || 1,
        total_pages: data.total_pages || Math.ceil((data.count || 0) / (params.page_size || 50)),
        page_size: data.page_size || params.page_size || 50
      }
    }
  } catch (error) {
    console.error('Error obteniendo historial de logins:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener el historial de logins'

    throw new Error(errorMessage)
  }
}

/**
 * Obtiene estadísticas de auditoría
 * @param {Object} params - Parámetros de consulta
 * @param {string} params.fecha_desde - Fecha inicio (YYYY-MM-DD)
 * @param {string} params.fecha_hasta - Fecha fin (YYYY-MM-DD)
 * @returns {Promise<Object>} - Estadísticas de auditoría normalizadas
 */
export async function getAuditStats(params = {}) {
  try {
    const data = await apiGet(API_ENDPOINTS.stats, params)
    
    // Normalize response
    return {
      success: true,
      data: {
        activity_log: data.activity_log || {},
        login_history: data.login_history || {},
        period: {
          fecha_desde: params.fecha_desde || null,
          fecha_hasta: params.fecha_hasta || null
        }
      }
    }
  } catch (error) {
    console.error('Error obteniendo estadísticas de auditoría:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener las estadísticas de auditoría'

    throw new Error(errorMessage)
  }
}

/**
 * Tipos de acciones de auditoría
 */
export const AUDIT_ACTION_TYPES = {
  LOGIN: 'login',
  LOGOUT: 'logout',
  CREATE: 'create',
  UPDATE: 'update',
  DELETE: 'delete',
  VIEW: 'view',
  DOWNLOAD: 'download',
  UPLOAD: 'upload',
  EXPORT: 'export',
  IMPORT: 'import',
  TRAIN: 'train',
  PREDICT: 'predict'
}

/**
 * Niveles de severidad de logs
 */
export const AUDIT_SEVERITY_LEVELS = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'critical'
}

/**
 * Formatea un log de actividad para visualización
 * @param {Object} log - Log a formatear
 * @returns {Object} - Log formateado
 */
export function formatActivityLog(log) {
  return {
    id: log.id,
    usuario: log.usuario,
    usuario_nombre: log.usuario_nombre || 'Usuario desconocido',
    accion: log.accion,
    descripcion: log.descripcion,
    direccion_ip: log.direccion_ip,
    user_agent: log.user_agent,
    fecha: log.fecha,
    // Formatear fecha para visualización
    fecha_formateada: new Date(log.fecha).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }),
    // Indicador de reciente (última hora)
    es_reciente: new Date(log.fecha) > new Date(Date.now() - 60 * 60 * 1000),
    // Datos adicionales
    metadata: log.metadata || {}
  }
}

/**
 * Formatea un registro de login para visualización
 * @param {Object} login - Registro de login a formatear
 * @returns {Object} - Registro formateado
 */
export function formatLoginHistory(login) {
  return {
    id: login.id,
    usuario: login.usuario,
    usuario_nombre: login.usuario_nombre || 'Usuario desconocido',
    exitoso: login.exitoso,
    direccion_ip: login.direccion_ip,
    user_agent: login.user_agent,
    razon_falla: login.razon_falla,
    fecha: login.fecha,
    // Formatear fecha para visualización
    fecha_formateada: new Date(login.fecha).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }),
    // Indicador de reciente (última hora)
    es_reciente: new Date(login.fecha) > new Date(Date.now() - 60 * 60 * 1000),
    // Estado visual
    estado_visual: login.exitoso ? 'success' : 'danger',
    icono: login.exitoso ? 'check-circle' : 'times-circle'
  }
}

/**
 * Valida parámetros de filtro de fecha
 * @param {Object} params - Parámetros a validar
 * @returns {Object} - Resultado de la validación
 */
export function validateDateFilters(params) {
  const errors = []

  if (params.fecha_desde && params.fecha_hasta) {
    const fechaDesde = new Date(params.fecha_desde)
    const fechaHasta = new Date(params.fecha_hasta)

    if (fechaDesde > fechaHasta) {
      errors.push('La fecha de inicio no puede ser posterior a la fecha de fin')
    }

    // Validar que no sea un rango muy grande (máximo 1 año)
    const diffMs = fechaHasta - fechaDesde
    const diffDays = diffMs / (1000 * 60 * 60 * 24)
    
    if (diffDays > 365) {
      errors.push('El rango de fechas no puede exceder 1 año')
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Genera reporte de auditoría en formato específico
 * @param {Object} params - Parámetros del reporte
 * @param {string} params.tipo - Tipo de reporte ('activity' o 'login')
 * @param {string} params.formato - Formato del reporte ('csv', 'json', 'pdf')
 * @param {string} params.fecha_desde - Fecha inicio
 * @param {string} params.fecha_hasta - Fecha fin
 * @returns {Promise<Object>} - Resultado de la generación
 */
export async function generateAuditReport(params) {
  try {
    console.log('📄 Generando reporte de auditoría:', params)

    // Determinar endpoint según tipo
    const endpoint = params.tipo === 'login' 
      ? `${API_ENDPOINTS.loginHistory}export/`
      : `${API_ENDPOINTS.activityLogs}export/`

    const response = await api.get(endpoint, {
      params: {
        formato: params.formato,
        fecha_desde: params.fecha_desde,
        fecha_hasta: params.fecha_hasta
      },
      responseType: params.formato === 'pdf' ? 'blob' : 'json'
    })

    console.log('✅ Reporte de auditoría generado')

    // Si es blob (PDF), crear URL de descarga
    if (params.formato === 'pdf') {
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = globalThis.URL.createObjectURL(blob)
      
      return {
        success: true,
        data: {
          url,
          filename: `auditoria_${params.tipo}_${new Date().toISOString().split('T')[0]}.pdf`
        }
      }
    }

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error generando reporte de auditoría:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al generar el reporte de auditoría'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Obtiene resumen de actividad por usuario
 * @param {number} userId - ID del usuario
 * @param {Object} params - Parámetros adicionales
 * @returns {Promise<Object>} - Resumen de actividad
 */
export async function getUserActivitySummary(userId, params = {}) {
  try {
    if (!userId) {
      throw new Error('ID de usuario requerido')
    }

    console.log('📊 Obteniendo resumen de actividad del usuario:', userId)

    const response = await api.get(`/audit/users/${userId}/summary/`, { params })

    console.log('✅ Resumen de actividad obtenido')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo resumen de actividad:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener el resumen de actividad'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Configuración del servicio de auditoría
 */
export const AUDIT_CONFIG = {
  // Intervalo de actualización de logs (ms)
  LOGS_REFRESH_INTERVAL: 30000, // 30 segundos
  
  // Tamaño de página por defecto
  DEFAULT_PAGE_SIZE: 50,
  
  // Colores por tipo de acción
  ACTION_COLORS: {
    login: 'blue',
    logout: 'gray',
    create: 'green',
    update: 'yellow',
    delete: 'red',
    view: 'info',
    download: 'purple',
    upload: 'orange',
    export: 'teal',
    import: 'cyan',
    train: 'indigo',
    predict: 'pink'
  },
  
  // Iconos por tipo de acción
  ACTION_ICONS: {
    login: 'sign-in-alt',
    logout: 'sign-out-alt',
    create: 'plus-circle',
    update: 'edit',
    delete: 'trash',
    view: 'eye',
    download: 'download',
    upload: 'upload',
    export: 'file-export',
    import: 'file-import',
    train: 'cogs',
    predict: 'brain'
  }
}

// Exportación por defecto
export default {
  getActivityLogs,
  getLoginHistory,
  getAuditStats,
  generateAuditReport,
  getUserActivitySummary,
  formatActivityLog,
  formatLoginHistory,
  validateDateFilters,
  AUDIT_ACTION_TYPES,
  AUDIT_SEVERITY_LEVELS,
  AUDIT_CONFIG
}


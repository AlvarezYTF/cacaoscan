/**
 * Servicio API para gestión de notificaciones
 * 
 * Maneja todas las operaciones relacionadas con el sistema de notificaciones:
 * - Obtener lista de notificaciones
 * - Marcar como leídas
 * - Contador de no leídas
 * - Estadísticas
 */

import api from './api'

// Endpoints de la API
const API_ENDPOINTS = {
  list: '/notifications/',
  detail: (id) => `/notifications/${id}/`,
  markRead: (id) => `/notifications/${id}/read/`,
  markAllRead: '/notifications/mark-all-read/',
  unreadCount: '/notifications/unread-count/',
  stats: '/notifications/stats/',
  create: '/notifications/create/'
}

/**
 * Obtiene lista de notificaciones del usuario actual
 * @param {Object} params - Parámetros de consulta
 * @param {number} params.page - Página actual
 * @param {number} params.page_size - Tamaño de página
 * @param {boolean} params.leida - Filtrar por leídas/no leídas
 * @param {string} params.tipo - Tipo de notificación
 * @returns {Promise<Object>} - Lista paginada de notificaciones
 */
export async function getNotifications(params = {}) {
  try {
    console.log('📬 Obteniendo notificaciones:', params)

    const response = await api.get(API_ENDPOINTS.list, { params })

    console.log('✅ Notificaciones obtenidas:', {
      count: response.data.count || 0,
      results: response.data.results?.length || 0
    })

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo notificaciones:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener las notificaciones'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Obtiene detalle de una notificación específica
 * @param {number} notificationId - ID de la notificación
 * @returns {Promise<Object>} - Detalle de la notificación
 */
export async function getNotificationDetail(notificationId) {
  try {
    if (!notificationId) {
      throw new Error('ID de notificación requerido')
    }

    console.log('🔍 Obteniendo detalle de notificación:', notificationId)

    const response = await api.get(API_ENDPOINTS.detail(notificationId))

    console.log('✅ Detalle de notificación obtenido')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo detalle de notificación:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener el detalle de la notificación'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Marca una notificación como leída
 * @param {number} notificationId - ID de la notificación
 * @returns {Promise<Object>} - Resultado de la operación
 */
export async function markNotificationAsRead(notificationId) {
  try {
    if (!notificationId) {
      throw new Error('ID de notificación requerido')
    }

    console.log('✓ Marcando notificación como leída:', notificationId)

    const response = await api.post(API_ENDPOINTS.markRead(notificationId))

    console.log('✅ Notificación marcada como leída')

    return {
      success: true,
      data: response.data,
      message: 'Notificación marcada como leída'
    }

  } catch (error) {
    console.error('❌ Error marcando notificación:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al marcar la notificación como leída'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Marca todas las notificaciones como leídas
 * @returns {Promise<Object>} - Resultado de la operación
 */
export async function markAllNotificationsAsRead() {
  try {
    console.log('✓ Marcando todas las notificaciones como leídas')

    const response = await api.post(API_ENDPOINTS.markAllRead)

    console.log('✅ Todas las notificaciones marcadas como leídas')

    return {
      success: true,
      data: response.data,
      message: 'Todas las notificaciones han sido marcadas como leídas'
    }

  } catch (error) {
    console.error('❌ Error marcando todas las notificaciones:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al marcar todas las notificaciones como leídas'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Obtiene el contador de notificaciones no leídas
 * @returns {Promise<Object>} - Contador de no leídas
 */
export async function getUnreadNotificationsCount() {
  try {
    const response = await api.get(API_ENDPOINTS.unreadCount)

    const count = response.data.unread_count || 0

    return {
      success: true,
      data: {
        unread_count: count
      }
    }

  } catch (error) {
    console.error('❌ Error obteniendo contador de notificaciones:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener el contador de notificaciones'

    return {
      success: false,
      error: errorMessage,
      data: {
        unread_count: 0
      }
    }
  }
}

/**
 * Obtiene estadísticas de notificaciones
 * @returns {Promise<Object>} - Estadísticas de notificaciones
 */
export async function getNotificationsStats() {
  try {
    console.log('📊 Obteniendo estadísticas de notificaciones')

    const response = await api.get(API_ENDPOINTS.stats)

    console.log('✅ Estadísticas obtenidas')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo estadísticas de notificaciones:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener las estadísticas de notificaciones'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Crea una nueva notificación (solo para admin)
 * @param {Object} notificationData - Datos de la notificación
 * @param {string} notificationData.titulo - Título de la notificación
 * @param {string} notificationData.mensaje - Mensaje de la notificación
 * @param {string} notificationData.tipo - Tipo de notificación (info, warning, error, success)
 * @param {number} notificationData.usuario - ID del usuario destinatario (opcional para broadcast)
 * @returns {Promise<Object>} - Notificación creada
 */
export async function createNotification(notificationData) {
  try {
    console.log('➕ Creando nueva notificación:', notificationData)

    const response = await api.post(API_ENDPOINTS.create, notificationData)

    console.log('✅ Notificación creada exitosamente')

    return {
      success: true,
      data: response.data,
      message: 'Notificación creada exitosamente'
    }

  } catch (error) {
    console.error('❌ Error creando notificación:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al crear la notificación'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Tipos de notificación disponibles
 */
export const NOTIFICATION_TYPES = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  SUCCESS: 'success'
}

/**
 * Valida datos de notificación antes de envío
 * @param {Object} notificationData - Datos a validar
 * @returns {Object} - Resultado de la validación
 */
export function validateNotificationData(notificationData) {
  const errors = []

  if (!notificationData.titulo || notificationData.titulo.trim().length === 0) {
    errors.push('El título es requerido')
  } else if (notificationData.titulo.length > 200) {
    errors.push('El título no puede exceder 200 caracteres')
  }

  if (!notificationData.mensaje || notificationData.mensaje.trim().length === 0) {
    errors.push('El mensaje es requerido')
  } else if (notificationData.mensaje.length > 1000) {
    errors.push('El mensaje no puede exceder 1000 caracteres')
  }

  if (notificationData.tipo && !Object.values(NOTIFICATION_TYPES).includes(notificationData.tipo)) {
    errors.push('Tipo de notificación inválido')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Formatea una notificación para visualización
 * @param {Object} notification - Notificación a formatear
 * @returns {Object} - Notificación formateada
 */
export function formatNotification(notification) {
  return {
    id: notification.id,
    titulo: notification.titulo,
    mensaje: notification.mensaje,
    tipo: notification.tipo || 'info',
    leida: notification.leida || false,
    fecha_creacion: notification.fecha_creacion,
    fecha_leida: notification.fecha_leida,
    // Formatear fecha para visualización
    fecha_formateada: new Date(notification.fecha_creacion).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }),
    // Indicador de reciente (últimas 24 horas)
    es_reciente: new Date(notification.fecha_creacion) > new Date(Date.now() - 24 * 60 * 60 * 1000)
  }
}

/**
 * Configuración del servicio
 */
export const NOTIFICATIONS_CONFIG = {
  // Intervalo de actualización del contador (ms)
  UNREAD_COUNT_REFRESH_INTERVAL: 30000, // 30 segundos
  
  // Intervalo de actualización de lista (ms)
  LIST_REFRESH_INTERVAL: 60000, // 1 minuto
  
  // Tamaño de página por defecto
  DEFAULT_PAGE_SIZE: 20,
  
  // Colores por tipo
  TYPE_COLORS: {
    info: 'blue',
    warning: 'yellow',
    error: 'red',
    success: 'green'
  },
  
  // Iconos por tipo
  TYPE_ICONS: {
    info: 'info-circle',
    warning: 'exclamation-triangle',
    error: 'times-circle',
    success: 'check-circle'
  }
}

// Exportación por defecto
export default {
  getNotifications,
  getNotificationDetail,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  getUnreadNotificationsCount,
  getNotificationsStats,
  createNotification,
  validateNotificationData,
  formatNotification,
  NOTIFICATION_TYPES,
  NOTIFICATIONS_CONFIG
}


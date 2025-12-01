import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useWebSocketBase } from './useWebSocketBase'

export function useWebSocket() {
  // Deshabilitar WebSockets en modo desarrollo para evitar reconexiones infinitas
  if (import.meta.env.MODE === 'development') {
    console.log('🔌 WebSockets deshabilitados en modo desarrollo')
    
    // Retornar un objeto mock con la misma interfaz
    return {
      isConnected: ref(false),
      isConnecting: ref(false),
      connectionError: ref(null),
      connectionStatus: computed(() => 'disabled'),
      hasAnyConnection: computed(() => false),
      lastMessage: ref(null),
      messageHistory: ref([]),
      reconnectAttempts: ref(0),
      connect: () => {},
      disconnect: () => {},
      reconnect: () => {},
      ping: () => {},
      markNotificationRead: () => {},
      markAllNotificationsRead: () => {},
      getNotificationStats: () => {},
      getAuditStats: () => {},
      getRecentActivity: () => {},
      getSystemStatus: () => {},
      getUserStats: () => {},
      on: () => {},
      off: () => {},
      emit: () => {}
    }
  }
  
  const authStore = useAuthStore()
  
  // Convertir HTTP/HTTPS a WS/WSS usando configuración centralizada
  const getWebSocketUrl = () => {
    if (import.meta.env.VITE_WS_URL) {
      return import.meta.env.VITE_WS_URL
    }
    // Usar runtime injection si está disponible
    if (typeof globalThis !== 'undefined' && globalThis.__API_BASE_URL__) {
      const apiUrl = globalThis.__API_BASE_URL__.replace(/\/api\/v1\/?$/, '')
      return apiUrl.replace(/^https?/, 'ws') + '/ws'
    }
    // Usar build-time variable
    if (import.meta.env.VITE_API_BASE_URL) {
      const apiUrl = import.meta.env.VITE_API_BASE_URL.replace(/\/api\/v1\/?$/, '')
      return apiUrl.replace(/^https?/, 'ws') + '/ws'
    }
    // Fallback para desarrollo
    return 'ws://localhost:8000/ws'
  }
  
  // Configuración
  const wsConfig = {
    baseUrl: getWebSocketUrl(),
    heartbeatInterval: 30000, // 30 segundos
    reconnectDelay: 5000, // 5 segundos
    maxMessageHistory: 100
  }
  
  // Event emitter simple
  const listeners = new Map()
  
  const emit = (event, data) => {
    if (listeners.has(event)) {
      for (const callback of listeners.get(event)) {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error en listener de evento ${event}:`, error)
        }
      }
    }
  }
  
  const on = (event, callback) => {
    if (!listeners.has(event)) {
      listeners.set(event, [])
    }
    listeners.get(event).push(callback)
  }
  
  const off = (event, callback) => {
    if (listeners.has(event)) {
      const callbacks = listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }
  
  // Helper para agregar mensaje al historial
  const addToHistory = (message) => {
    messageHistory.value.unshift({
      ...message,
      timestamp: new Date().toISOString()
    })
    
    // Limitar historial
    if (messageHistory.value.length > wsConfig.maxMessageHistory) {
      messageHistory.value = messageHistory.value.slice(0, wsConfig.maxMessageHistory)
    }
  }
  
  // Base message handler (extracted common logic)
  const createMessageHandler = (eventMap, logContext) => {
    return (data) => {
      lastMessage.value = data
      addToHistory(data)
      
      // Handle pong responses
      if (data.type === 'pong') {
        return
      }
      
      // Emit mapped events
      const eventName = eventMap[data.type]
      if (eventName) {
        emit(eventName, data.data)
      } else {
        console.log(`Mensaje de ${logContext} no manejado:`, data)
      }
    }
  }
  
  // Handlers de mensajes específicos
  const handleNotificationMessage = createMessageHandler({
    notification: 'notification-received',
    notification_update: 'notification-updated',
    stats_update: 'notification-stats-updated',
    pending_notification: 'pending-notification'
  }, 'notificación')
  
  const handleSystemStatusMessage = createMessageHandler({
    system_status: 'system-status-updated',
    system_alert: 'system-alert'
  }, 'estado del sistema')
  
  const handleAuditMessage = createMessageHandler({
    audit_activity: 'audit-activity',
    audit_login: 'audit-login',
    audit_stats_update: 'audit-stats-updated'
  }, 'auditoría')
  
  const handleUserStatsMessage = createMessageHandler({
    user_stats: 'user-stats-updated',
    user_stats_update: 'user-stats-updated'
  }, 'estadísticas de usuarios')
  
  // Estado compartido
  const lastMessage = ref(null)
  const messageHistory = ref([])
  
  
  // Estado agregado
  const connectionError = ref(null)
  
  // Computed
  const connectionStatus = computed(() => {
    if (notificationSocket.isConnecting.value || 
        systemStatusSocket.isConnecting.value || 
        auditSocket.isConnecting.value || 
        userStatsSocket.isConnecting.value) {
      return 'connecting'
    }
    if (hasAnyConnection.value) {
      return 'connected'
    }
    if (connectionError.value) {
      return 'error'
    }
    return 'disconnected'
  })
  
  const hasAnyConnection = computed(() => {
    return (notificationSocket?.isConnected.value) ||
           (systemStatusSocket?.isConnected.value) ||
           (auditSocket?.isConnected.value) ||
           (userStatsSocket?.isConnected.value)
  })
  
  const reconnectAttempts = computed(() => {
    const attempts = []
    if (notificationSocket) attempts.push(notificationSocket.reconnectAttempts.value)
    if (systemStatusSocket) attempts.push(systemStatusSocket.reconnectAttempts.value)
    if (auditSocket) attempts.push(auditSocket.reconnectAttempts.value)
    if (userStatsSocket) attempts.push(userStatsSocket.reconnectAttempts.value)
    return attempts.length > 0 ? Math.max(...attempts) : 0
  })
  
  // Referencias a las conexiones (se crean dinámicamente en connect)
  let notificationSocket = null
  let systemStatusSocket = null
  let auditSocket = null
  let userStatsSocket = null
  
  // Métodos principales
  const connect = () => {
    if (!authStore.user) {
      console.warn('No hay usuario autenticado, no se puede conectar WebSocket')
      return
    }
    
    connectionError.value = null
    
    try {
      // Desconectar conexiones existentes
      disconnect()
      
      // Crear conexión de notificaciones
      const notificationUrl = `${wsConfig.baseUrl}/notifications/${authStore.user.id}/`
      notificationSocket = useWebSocketBase({
        url: notificationUrl,
        onMessage: handleNotificationMessage,
        onError: (error) => {
          connectionError.value = 'Error de conexión de notificaciones'
          emit('connection-error', { type: 'notifications', error })
        },
        reconnectInterval: wsConfig.reconnectDelay,
        maxReconnectAttempts: 5
      })
      notificationSocket.connect()
      
      // Crear conexión de estado del sistema
      const systemStatusUrl = `${wsConfig.baseUrl}/system-status/`
      systemStatusSocket = useWebSocketBase({
        url: systemStatusUrl,
        onMessage: handleSystemStatusMessage,
        onError: (error) => {
          emit('connection-error', { type: 'system-status', error })
        },
        reconnectInterval: wsConfig.reconnectDelay,
        maxReconnectAttempts: 5
      })
      systemStatusSocket.connect()
      
      // Crear conexión de auditoría (solo para admins)
      if (authStore.user.is_superuser || authStore.user.is_staff) {
        const auditUrl = `${wsConfig.baseUrl}/audit/${authStore.user.id}/`
        auditSocket = useWebSocketBase({
          url: auditUrl,
          onMessage: handleAuditMessage,
          onError: (error) => {
            emit('connection-error', { type: 'audit', error })
          },
          reconnectInterval: wsConfig.reconnectDelay,
          maxReconnectAttempts: 5
        })
        auditSocket.connect()
      }
      
      // Crear conexión de estadísticas de usuarios
      const userStatsUrl = `${wsConfig.baseUrl}/user-stats/`
      userStatsSocket = useWebSocketBase({
        url: userStatsUrl,
        onMessage: handleUserStatsMessage,
        onError: (error) => {
          emit('connection-error', { type: 'user-stats', error })
        },
        reconnectInterval: wsConfig.reconnectDelay,
        maxReconnectAttempts: 5
      })
      userStatsSocket.connect()
      
    } catch (error) {
      console.error('Error conectando WebSockets:', error)
      connectionError.value = error.message
    }
  }
  
  const disconnect = () => {
    if (notificationSocket) {
      notificationSocket.disconnect()
      notificationSocket = null
    }
    if (systemStatusSocket) {
      systemStatusSocket.disconnect()
      systemStatusSocket = null
    }
    if (auditSocket) {
      auditSocket.disconnect()
      auditSocket = null
    }
    if (userStatsSocket) {
      userStatsSocket.disconnect()
      userStatsSocket = null
    }
    connectionError.value = null
  }
  
  const reconnect = () => {
    disconnect()
    setTimeout(() => {
      connect()
    }, wsConfig.reconnectDelay)
  }
  
  const ping = () => {
    const pingMessage = {
      type: 'ping',
      timestamp: new Date().toISOString()
    }
    
    if (notificationSocket) notificationSocket.send(pingMessage)
    if (systemStatusSocket) systemStatusSocket.send(pingMessage)
    if (auditSocket) auditSocket.send(pingMessage)
    if (userStatsSocket) userStatsSocket.send(pingMessage)
  }
  
  // Métodos específicos de notificaciones
  const markNotificationRead = (notificationId) => {
    if (notificationSocket) {
      notificationSocket.send({
        type: 'mark_read',
        notification_id: notificationId
      })
    }
  }
  
  const markAllNotificationsRead = () => {
    if (notificationSocket) {
      notificationSocket.send({
        type: 'mark_all_read'
      })
    }
  }
  
  const getNotificationStats = () => {
    if (notificationSocket) {
      notificationSocket.send({
        type: 'get_stats'
      })
    }
  }
  
  // Métodos específicos de auditoría
  const getAuditStats = () => {
    if (auditSocket) {
      auditSocket.send({
        type: 'get_audit_stats'
      })
    }
  }
  
  const getRecentActivity = () => {
    if (auditSocket) {
      auditSocket.send({
        type: 'get_recent_activity'
      })
    }
  }
  
  // Métodos específicos de sistema
  const getSystemStatus = () => {
    if (systemStatusSocket) {
      systemStatusSocket.send({
        type: 'get_status'
      })
    }
  }
  
  // Métodos específicos de usuarios
  const getUserStats = () => {
    if (userStatsSocket) {
      userStatsSocket.send({
        type: 'get_stats'
      })
    }
  }
  
  // Computed para estado agregado
  const isConnected = computed(() => hasAnyConnection.value)
  const isConnecting = computed(() => 
    (notificationSocket?.isConnecting.value) ||
    (systemStatusSocket?.isConnecting.value) ||
    (auditSocket?.isConnecting.value) ||
    (userStatsSocket?.isConnecting.value)
  )
  
  // Lifecycle
  onMounted(() => {
    // Solo conectar WebSockets si están habilitados (evitar reconexiones infinitas)
    const wsEnabled = import.meta.env.VITE_WS_ENABLED !== 'false'
    
    if (wsEnabled) {
      // Configurar heartbeat solo si hay conexión
      let heartbeatInterval = null
      
      const startHeartbeat = () => {
        if (heartbeatInterval) return
        
        heartbeatInterval = setInterval(() => {
          if (hasAnyConnection.value) {
            try {
              ping()
            } catch (error) {
              console.error('Error en heartbeat:', error)
              if (heartbeatInterval) {
                clearInterval(heartbeatInterval)
                heartbeatInterval = null
              }
            }
          }
        }, wsConfig.heartbeatInterval)
      }
      
      // Iniciar heartbeat después de un delay
      setTimeout(() => {
        startHeartbeat()
      }, 2000)
      
      // Limpiar al desmontar
      onUnmounted(() => {
        if (heartbeatInterval) {
          clearInterval(heartbeatInterval)
          heartbeatInterval = null
        }
        disconnect()
      })
    }
  })
  
  // Watchers
  watch(() => authStore.user, (newUser, oldUser) => {
    if (newUser && !oldUser) {
      // Usuario logueado, intentar conectar
      // Usar setTimeout para evitar errores inmediatos si el servidor no está listo
      setTimeout(() => {
        try {
          connect()
        } catch (error) {
          console.warn('⚠️ No se pudieron conectar los WebSockets. La aplicación seguirá funcionando sin actualizaciones en tiempo real:', error.message)
          connectionError.value = 'WebSockets no disponibles (modo offline)'
        }
      }, 1000)
    } else if (!newUser && oldUser) {
      // Usuario deslogueado, desconectar
      disconnect()
    }
  }, { immediate: true })
  
  return {
    // Estado
    isConnected,
    isConnecting,
    connectionError,
    connectionStatus,
    hasAnyConnection,
    lastMessage,
    messageHistory,
    reconnectAttempts,
    
    // Métodos
    connect,
    disconnect,
    reconnect,
    ping,
    
    // Notificaciones
    markNotificationRead,
    markAllNotificationsRead,
    getNotificationStats,
    
    // Auditoría
    getAuditStats,
    getRecentActivity,
    
    // Sistema
    getSystemStatus,
    
    // Usuarios
    getUserStats,
    
    // Eventos
    on,
    off,
    emit
  }
}

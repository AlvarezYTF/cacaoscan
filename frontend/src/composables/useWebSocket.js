import { ref, computed, reactive, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useWebSocketBase } from './useWebSocketBase'

export function useWebSocket() {
  // Deshabilitar WebSockets en modo desarrollo para evitar reconexiones infinitas
  if (import.meta.env.MODE === 'development') {
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
      notificationSocket: null,
      systemStatusSocket: null,
      auditSocket: null,
      userStatsSocket: null,
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
    if (socketRefs.notificationSocket?.isConnecting.value || 
        socketRefs.systemStatusSocket?.isConnecting.value || 
        socketRefs.auditSocket?.isConnecting.value || 
        socketRefs.userStatsSocket?.isConnecting.value) {
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
    return !!(socketRefs.notificationSocket?.isConnected.value) ||
           !!(socketRefs.systemStatusSocket?.isConnected.value) ||
           !!(socketRefs.auditSocket?.isConnected.value) ||
           !!(socketRefs.userStatsSocket?.isConnected.value)
  })
  
  const reconnectAttempts = computed(() => {
    const attempts = []
    if (socketRefs.notificationSocket) attempts.push(socketRefs.notificationSocket.reconnectAttempts.value)
    if (socketRefs.systemStatusSocket) attempts.push(socketRefs.systemStatusSocket.reconnectAttempts.value)
    if (socketRefs.auditSocket) attempts.push(socketRefs.auditSocket.reconnectAttempts.value)
    if (socketRefs.userStatsSocket) attempts.push(socketRefs.userStatsSocket.reconnectAttempts.value)
    return attempts.length > 0 ? Math.max(...attempts) : 0
  })
  
  // Referencias a las conexiones (se crean dinámicamente en connect)
  // Using reactive object to allow mutation in tests and maintain reactivity
  const socketRefs = reactive({
    notificationSocket: null,
    systemStatusSocket: null,
    auditSocket: null,
    userStatsSocket: null
  })
  
  // Aliases para compatibilidad con código existente
  let notificationSocket = null
  let systemStatusSocket = null
  let auditSocket = null
  let userStatsSocket = null
  
  // Métodos principales
  const connect = () => {
    if (!authStore.user) {
      return
    }
    
    connectionError.value = null
    
    try {
      // Desconectar conexiones existentes
      internalMethods.disconnect()
      
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
      socketRefs.notificationSocket = notificationSocket
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
      socketRefs.systemStatusSocket = systemStatusSocket
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
        socketRefs.auditSocket = auditSocket
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
      socketRefs.userStatsSocket = userStatsSocket
      userStatsSocket.connect()
      
    } catch (error) {
      connectionError.value = error.message
    }
  }
  
  const disconnect = () => {
    if (socketRefs.notificationSocket) {
      socketRefs.notificationSocket.disconnect()
      notificationSocket = null
      socketRefs.notificationSocket = null
    }
    if (socketRefs.systemStatusSocket) {
      socketRefs.systemStatusSocket.disconnect()
      systemStatusSocket = null
      socketRefs.systemStatusSocket = null
    }
    if (socketRefs.auditSocket) {
      socketRefs.auditSocket.disconnect()
      auditSocket = null
      socketRefs.auditSocket = null
    }
    if (socketRefs.userStatsSocket) {
      socketRefs.userStatsSocket.disconnect()
      userStatsSocket = null
      socketRefs.userStatsSocket = null
    }
    connectionError.value = null
  }
  
  // Internal method references for reconnect to use (allows mocking in tests)
  const internalMethods = {
    disconnect,
    connect
  }
  
  const reconnect = () => {
    internalMethods.disconnect()
    setTimeout(() => {
      internalMethods.connect()
    }, wsConfig.reconnectDelay)
  }
  
  const ping = () => {
    const pingMessage = {
      type: 'ping',
      timestamp: new Date().toISOString()
    }
    
    // Use socketRefs to allow mutation in tests
    const sockets = [
      socketRefs.notificationSocket,
      socketRefs.systemStatusSocket,
      socketRefs.auditSocket,
      socketRefs.userStatsSocket
    ]
    
    for (const socket of sockets) {
      if (socket) {
        socket.send(pingMessage)
      }
    }
  }
  
  // Métodos específicos de notificaciones
  const markNotificationRead = (notificationId) => {
    if (socketRefs.notificationSocket) {
      socketRefs.notificationSocket.send({
        type: 'mark_read',
        notification_id: notificationId
      })
    }
  }
  
  const markAllNotificationsRead = () => {
    if (socketRefs.notificationSocket) {
      socketRefs.notificationSocket.send({
        type: 'mark_all_read'
      })
    }
  }
  
  const getNotificationStats = () => {
    if (socketRefs.notificationSocket) {
      socketRefs.notificationSocket.send({
        type: 'get_stats'
      })
    }
  }
  
  // Métodos específicos de auditoría
  const getAuditStats = () => {
    if (socketRefs.auditSocket) {
      socketRefs.auditSocket.send({
        type: 'get_audit_stats'
      })
    }
  }
  
  const getRecentActivity = () => {
    if (socketRefs.auditSocket) {
      socketRefs.auditSocket.send({
        type: 'get_recent_activity'
      })
    }
  }
  
  // Métodos específicos de sistema
  const getSystemStatus = () => {
    if (socketRefs.systemStatusSocket) {
      socketRefs.systemStatusSocket.send({
        type: 'get_status'
      })
    }
  }
  
  // Métodos específicos de usuarios
  const getUserStats = () => {
    if (socketRefs.userStatsSocket) {
      socketRefs.userStatsSocket.send({
        type: 'get_stats'
      })
    }
  }
  
  // Computed para estado agregado
  const isConnected = computed(() => hasAnyConnection.value)
  const isConnecting = computed(() => 
    (socketRefs.notificationSocket?.isConnecting.value) ||
    (socketRefs.systemStatusSocket?.isConnecting.value) ||
    (socketRefs.auditSocket?.isConnecting.value) ||
    (socketRefs.userStatsSocket?.isConnecting.value)
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
        internalMethods.disconnect()
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
          connectionError.value = 'WebSockets no disponibles (modo offline)'
        }
      }, 1000)
    } else if (!newUser && oldUser) {
      // Usuario deslogueado, desconectar
      internalMethods.disconnect()
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
    
    // Referencias a sockets (para testing)
    get notificationSocket() { return socketRefs.notificationSocket },
    set notificationSocket(value) { 
      socketRefs.notificationSocket = value
    },
    get systemStatusSocket() { return socketRefs.systemStatusSocket },
    set systemStatusSocket(value) { 
      socketRefs.systemStatusSocket = value
    },
    get auditSocket() { return socketRefs.auditSocket },
    set auditSocket(value) { 
      socketRefs.auditSocket = value
    },
    get userStatsSocket() { return socketRefs.userStatsSocket },
    set userStatsSocket(value) { 
      socketRefs.userStatsSocket = value
    },
    
    // Métodos
    get connect() { return internalMethods.connect },
    set connect(value) { 
      internalMethods.connect = value
    },
    get disconnect() { return internalMethods.disconnect },
    set disconnect(value) { 
      internalMethods.disconnect = value
    },
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

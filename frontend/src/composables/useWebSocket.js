import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useWebSocket() {
  const authStore = useAuthStore()
  
  // Estado reactivo
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const connectionError = ref(null)
  const lastMessage = ref(null)
  const messageHistory = ref([])
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5
  const reconnectInterval = ref(null)
  
  // WebSocket instances
  const notificationSocket = ref(null)
  const systemStatusSocket = ref(null)
  const auditSocket = ref(null)
  
  // Configuración
  const wsConfig = {
    baseUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
    heartbeatInterval: 30000, // 30 segundos
    reconnectDelay: 5000, // 5 segundos
    maxMessageHistory: 100
  }
  
  // Computed
  const connectionStatus = computed(() => {
    if (isConnecting.value) return 'connecting'
    if (isConnected.value) return 'connected'
    if (connectionError.value) return 'error'
    return 'disconnected'
  })
  
  const hasAnyConnection = computed(() => {
    return notificationSocket.value?.readyState === WebSocket.OPEN ||
           systemStatusSocket.value?.readyState === WebSocket.OPEN ||
           auditSocket.value?.readyState === WebSocket.OPEN
  })
  
  // Métodos principales
  const connect = () => {
    if (!authStore.user) {
      console.warn('No hay usuario autenticado, no se puede conectar WebSocket')
      return
    }
    
    isConnecting.value = true
    connectionError.value = null
    
    try {
      // Conectar a notificaciones
      connectNotifications()
      
      // Conectar a estado del sistema
      connectSystemStatus()
      
      // Conectar a auditoría (solo para admins)
      if (authStore.user.is_superuser || authStore.user.is_staff) {
        connectAudit()
      }
      
    } catch (error) {
      console.error('Error conectando WebSockets:', error)
      connectionError.value = error.message
      isConnecting.value = false
    }
  }
  
  const disconnect = () => {
    // Desconectar todos los sockets
    if (notificationSocket.value) {
      notificationSocket.value.close()
      notificationSocket.value = null
    }
    
    if (systemStatusSocket.value) {
      systemStatusSocket.value.close()
      systemStatusSocket.value = null
    }
    
    if (auditSocket.value) {
      auditSocket.value.close()
      auditSocket.value = null
    }
    
    // Limpiar intervalos
    if (reconnectInterval.value) {
      clearInterval(reconnectInterval.value)
      reconnectInterval.value = null
    }
    
    isConnected.value = false
    isConnecting.value = false
    reconnectAttempts.value = 0
  }
  
  const reconnect = () => {
    if (reconnectAttempts.value >= maxReconnectAttempts) {
      console.error('Máximo número de intentos de reconexión alcanzado')
      return
    }
    
    reconnectAttempts.value++
    console.log(`Intentando reconectar... (${reconnectAttempts.value}/${maxReconnectAttempts})`)
    
    setTimeout(() => {
      disconnect()
      connect()
    }, wsConfig.reconnectDelay)
  }
  
  // Conexiones específicas
  const connectNotifications = () => {
    if (!authStore.user) return
    
    const url = `${wsConfig.baseUrl}/notifications/${authStore.user.id}/`
    notificationSocket.value = new WebSocket(url)
    
    notificationSocket.value.onopen = () => {
      console.log('WebSocket de notificaciones conectado')
      isConnected.value = true
      isConnecting.value = false
      reconnectAttempts.value = 0
    }
    
    notificationSocket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleNotificationMessage(data)
      } catch (error) {
        console.error('Error parseando mensaje de notificaciones:', error)
      }
    }
    
    notificationSocket.value.onclose = (event) => {
      console.log('WebSocket de notificaciones desconectado:', event.code, event.reason)
      isConnected.value = false
      
      if (!event.wasClean) {
        reconnect()
      }
    }
    
    notificationSocket.value.onerror = (error) => {
      console.error('Error en WebSocket de notificaciones:', error)
      connectionError.value = 'Error de conexión de notificaciones'
    }
  }
  
  const connectSystemStatus = () => {
    const url = `${wsConfig.baseUrl}/system-status/`
    systemStatusSocket.value = new WebSocket(url)
    
    systemStatusSocket.value.onopen = () => {
      console.log('WebSocket de estado del sistema conectado')
    }
    
    systemStatusSocket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleSystemStatusMessage(data)
      } catch (error) {
        console.error('Error parseando mensaje de estado del sistema:', error)
      }
    }
    
    systemStatusSocket.value.onclose = (event) => {
      console.log('WebSocket de estado del sistema desconectado:', event.code, event.reason)
    }
    
    systemStatusSocket.value.onerror = (error) => {
      console.error('Error en WebSocket de estado del sistema:', error)
    }
  }
  
  const connectAudit = () => {
    if (!authStore.user) return
    
    const url = `${wsConfig.baseUrl}/audit/${authStore.user.id}/`
    auditSocket.value = new WebSocket(url)
    
    auditSocket.value.onopen = () => {
      console.log('WebSocket de auditoría conectado')
    }
    
    auditSocket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleAuditMessage(data)
      } catch (error) {
        console.error('Error parseando mensaje de auditoría:', error)
      }
    }
    
    auditSocket.value.onclose = (event) => {
      console.log('WebSocket de auditoría desconectado:', event.code, event.reason)
    }
    
    auditSocket.value.onerror = (error) => {
      console.error('Error en WebSocket de auditoría:', error)
    }
  }
  
  // Manejo de mensajes
  const handleNotificationMessage = (data) => {
    lastMessage.value = data
    
    // Agregar al historial
    addToHistory(data)
    
    // Emitir eventos específicos
    switch (data.type) {
      case 'notification':
        emit('notification-received', data.data)
        break
      case 'notification_update':
        emit('notification-updated', data.data)
        break
      case 'stats_update':
        emit('notification-stats-updated', data.data)
        break
      case 'pending_notification':
        emit('pending-notification', data.data)
        break
      case 'pong':
        // Respuesta a ping
        break
      default:
        console.log('Mensaje de notificación no manejado:', data)
    }
  }
  
  const handleSystemStatusMessage = (data) => {
    lastMessage.value = data
    addToHistory(data)
    
    switch (data.type) {
      case 'system_status':
        emit('system-status-updated', data.data)
        break
      case 'system_alert':
        emit('system-alert', data.data)
        break
      case 'pong':
        // Respuesta a ping
        break
      default:
        console.log('Mensaje de estado del sistema no manejado:', data)
    }
  }
  
  const handleAuditMessage = (data) => {
    lastMessage.value = data
    addToHistory(data)
    
    switch (data.type) {
      case 'audit_activity':
        emit('audit-activity', data.data)
        break
      case 'audit_login':
        emit('audit-login', data.data)
        break
      case 'audit_stats_update':
        emit('audit-stats-updated', data.data)
        break
      case 'pong':
        // Respuesta a ping
        break
      default:
        console.log('Mensaje de auditoría no manejado:', data)
    }
  }
  
  // Utilidades
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
  
  const sendMessage = (socket, message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket no está conectado')
    }
  }
  
  const ping = () => {
    const pingMessage = {
      type: 'ping',
      timestamp: new Date().toISOString()
    }
    
    if (notificationSocket.value) {
      sendMessage(notificationSocket.value, pingMessage)
    }
    if (systemStatusSocket.value) {
      sendMessage(systemStatusSocket.value, pingMessage)
    }
    if (auditSocket.value) {
      sendMessage(auditSocket.value, pingMessage)
    }
  }
  
  const markNotificationRead = (notificationId) => {
    if (notificationSocket.value) {
      sendMessage(notificationSocket.value, {
        type: 'mark_read',
        notification_id: notificationId
      })
    }
  }
  
  const markAllNotificationsRead = () => {
    if (notificationSocket.value) {
      sendMessage(notificationSocket.value, {
        type: 'mark_all_read'
      })
    }
  }
  
  const getNotificationStats = () => {
    if (notificationSocket.value) {
      sendMessage(notificationSocket.value, {
        type: 'get_stats'
      })
    }
  }
  
  const getAuditStats = () => {
    if (auditSocket.value) {
      sendMessage(auditSocket.value, {
        type: 'get_audit_stats'
      })
    }
  }
  
  const getRecentActivity = () => {
    if (auditSocket.value) {
      sendMessage(auditSocket.value, {
        type: 'get_recent_activity'
      })
    }
  }
  
  const getSystemStatus = () => {
    if (systemStatusSocket.value) {
      sendMessage(systemStatusSocket.value, {
        type: 'get_status'
      })
    }
  }
  
  // Event emitter simple
  const listeners = new Map()
  
  const emit = (event, data) => {
    if (listeners.has(event)) {
      listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error en listener de evento ${event}:`, error)
        }
      })
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
  
  // Lifecycle
  onMounted(() => {
    // Configurar heartbeat
    const heartbeatInterval = setInterval(() => {
      if (hasAnyConnection.value) {
        ping()
      }
    }, wsConfig.heartbeatInterval)
    
    // Limpiar al desmontar
    onUnmounted(() => {
      clearInterval(heartbeatInterval)
      disconnect()
    })
  })
  
  // Watchers
  watch(() => authStore.user, (newUser, oldUser) => {
    if (newUser && !oldUser) {
      // Usuario logueado, conectar
      connect()
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
    
    // Eventos
    on,
    off,
    emit
  }
}

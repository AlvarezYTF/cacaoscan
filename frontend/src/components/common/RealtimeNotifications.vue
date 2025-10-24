<template>
  <div class="realtime-notifications">
    <!-- Indicador de conexión -->
    <div class="connection-indicator" :class="connectionStatus">
      <div class="indicator-dot"></div>
      <span class="indicator-text">{{ getConnectionText() }}</span>
    </div>

    <!-- Contador de notificaciones no leídas -->
    <div v-if="unreadCount > 0" class="notification-badge">
      <i class="fas fa-bell"></i>
      <span class="badge-count">{{ unreadCount }}</span>
    </div>

    <!-- Lista de notificaciones -->
    <div v-if="showNotifications" class="notifications-dropdown">
      <div class="dropdown-header">
        <h3>Notificaciones</h3>
        <div class="header-actions">
          <button
            @click="markAllAsRead"
            class="btn btn-sm btn-outline"
            :disabled="unreadCount === 0"
          >
            <i class="fas fa-check-double"></i>
            Marcar todas como leídas
          </button>
          <button
            @click="showNotifications = false"
            class="btn btn-sm btn-outline"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>

      <div class="notifications-list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-item"
          :class="{ 'unread': !notification.leida }"
          @click="handleNotificationClick(notification)"
        >
          <div class="notification-icon" :class="getNotificationClass(notification.tipo)">
            <i :class="getNotificationIcon(notification.tipo)"></i>
          </div>
          
          <div class="notification-content">
            <div class="notification-title">{{ notification.titulo }}</div>
            <div class="notification-message">{{ notification.mensaje }}</div>
            <div class="notification-time">{{ formatTime(notification.fecha_creacion) }}</div>
          </div>
          
          <div class="notification-actions">
            <button
              v-if="!notification.leida"
              @click.stop="markAsRead(notification.id)"
              class="btn btn-sm btn-outline"
              title="Marcar como leída"
            >
              <i class="fas fa-check"></i>
            </button>
          </div>
        </div>

        <div v-if="notifications.length === 0" class="no-notifications">
          <i class="fas fa-bell-slash"></i>
          <p>No hay notificaciones</p>
        </div>
      </div>

      <div class="dropdown-footer">
        <button
          @click="viewAllNotifications"
          class="btn btn-sm btn-primary"
        >
          <i class="fas fa-list"></i>
          Ver todas las notificaciones
        </button>
      </div>
    </div>

    <!-- Overlay para cerrar al hacer click fuera -->
    <div
      v-if="showNotifications"
      class="notifications-overlay"
      @click="showNotifications = false"
    ></div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWebSocket } from '@/composables/useWebSocket'
import { useNotificationsStore } from '@/stores/notifications'
import Swal from 'sweetalert2'

export default {
  name: 'RealtimeNotifications',
  setup() {
    const router = useRouter()
    const notificationsStore = useNotificationsStore()
    const websocket = useWebSocket()
    
    // Estado reactivo
    const showNotifications = ref(false)
    const notifications = ref([])
    const unreadCount = ref(0)
    
    // Computed
    const connectionStatus = computed(() => websocket.connectionStatus.value)
    
    // Métodos
    const getConnectionText = () => {
      switch (connectionStatus.value) {
        case 'connected':
          return 'Conectado'
        case 'connecting':
          return 'Conectando...'
        case 'error':
          return 'Error de conexión'
        default:
          return 'Desconectado'
      }
    }
    
    const getNotificationClass = (tipo) => {
      const classes = {
        'info': 'notification-info',
        'warning': 'notification-warning',
        'error': 'notification-error',
        'success': 'notification-success',
        'defect_alert': 'notification-alert',
        'report_ready': 'notification-info',
        'training_complete': 'notification-success',
        'welcome': 'notification-info'
      }
      return classes[tipo] || 'notification-info'
    }
    
    const getNotificationIcon = (tipo) => {
      const icons = {
        'info': 'fas fa-info-circle',
        'warning': 'fas fa-exclamation-triangle',
        'error': 'fas fa-times-circle',
        'success': 'fas fa-check-circle',
        'defect_alert': 'fas fa-exclamation-triangle',
        'report_ready': 'fas fa-file-alt',
        'training_complete': 'fas fa-brain',
        'welcome': 'fas fa-hand-wave'
      }
      return icons[tipo] || 'fas fa-bell'
    }
    
    const formatTime = (dateString) => {
      const date = new Date(dateString)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) { // Menos de 1 minuto
        return 'Hace un momento'
      } else if (diff < 3600000) { // Menos de 1 hora
        const minutes = Math.floor(diff / 60000)
        return `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}`
      } else if (diff < 86400000) { // Menos de 1 día
        const hours = Math.floor(diff / 3600000)
        return `Hace ${hours} hora${hours > 1 ? 's' : ''}`
      } else {
        return date.toLocaleDateString('es-ES', {
          day: 'numeric',
          month: 'short',
          hour: '2-digit',
          minute: '2-digit'
        })
      }
    }
    
    const handleNotificationClick = (notification) => {
      // Marcar como leída si no lo está
      if (!notification.leida) {
        markAsRead(notification.id)
      }
      
      // Navegar según el tipo de notificación
      if (notification.datos_extra) {
        const extra = notification.datos_extra
        
        if (extra.prediction_id) {
          router.push(`/analisis/${extra.prediction_id}`)
        } else if (extra.job_id) {
          router.push(`/entrenamiento/${extra.job_id}`)
        } else if (extra.finca_id) {
          router.push(`/fincas/${extra.finca_id}`)
        } else if (extra.lote_id) {
          router.push(`/lotes/${extra.lote_id}`)
        }
      }
      
      showNotifications.value = false
    }
    
    const markAsRead = (notificationId) => {
      websocket.markNotificationRead(notificationId)
      
      // Actualizar estado local
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification) {
        notification.leida = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    }
    
    const markAllAsRead = () => {
      websocket.markAllNotificationsRead()
      
      // Actualizar estado local
      notifications.value.forEach(notification => {
        notification.leida = true
      })
      unreadCount.value = 0
      
      Swal.fire({
        icon: 'success',
        title: 'Notificaciones marcadas como leídas',
        timer: 2000,
        showConfirmButton: false
      })
    }
    
    const viewAllNotifications = () => {
      router.push('/notificaciones')
      showNotifications.value = false
    }
    
    const loadNotifications = async () => {
      try {
        await notificationsStore.fetchNotifications()
        notifications.value = notificationsStore.notifications.slice(0, 10) // Últimas 10
        unreadCount.value = notificationsStore.unreadCount
      } catch (error) {
        console.error('Error cargando notificaciones:', error)
      }
    }
    
    const showNotificationToast = (notification) => {
      const toastConfig = {
        title: notification.titulo,
        text: notification.mensaje,
        timer: 5000,
        showConfirmButton: true,
        confirmButtonText: 'Ver',
        showCancelButton: true,
        cancelButtonText: 'Cerrar'
      }
      
      // Configurar icono según tipo
      switch (notification.tipo) {
        case 'success':
          toastConfig.icon = 'success'
          break
        case 'warning':
          toastConfig.icon = 'warning'
          break
        case 'error':
          toastConfig.icon = 'error'
          break
        default:
          toastConfig.icon = 'info'
      }
      
      Swal.fire(toastConfig).then((result) => {
        if (result.isConfirmed) {
          handleNotificationClick(notification)
        }
      })
    }
    
    // Event listeners
    const setupEventListeners = () => {
      // Nueva notificación recibida
      websocket.on('notification-received', (data) => {
        notifications.value.unshift(data)
        
        // Limitar a 10 notificaciones
        if (notifications.value.length > 10) {
          notifications.value = notifications.value.slice(0, 10)
        }
        
        // Incrementar contador si no está leída
        if (!data.leida) {
          unreadCount.value++
        }
        
        // Mostrar toast
        showNotificationToast(data)
      })
      
      // Notificación actualizada
      websocket.on('notification-updated', (data) => {
        const index = notifications.value.findIndex(n => n.id === data.id)
        if (index !== -1) {
          notifications.value[index] = data
        }
      })
      
      // Estadísticas actualizadas
      websocket.on('notification-stats-updated', (data) => {
        unreadCount.value = data.unread_count
      })
      
      // Notificación pendiente
      websocket.on('pending-notification', (data) => {
        notifications.value.unshift(data)
        
        if (notifications.value.length > 10) {
          notifications.value = notifications.value.slice(0, 10)
        }
        
        if (!data.leida) {
          unreadCount.value++
        }
      })
    }
    
    // Lifecycle
    onMounted(() => {
      setupEventListeners()
      loadNotifications()
      
      // Configurar click en el contador para mostrar notificaciones
      const notificationBadge = document.querySelector('.notification-badge')
      if (notificationBadge) {
        notificationBadge.addEventListener('click', () => {
          showNotifications.value = !showNotifications.value
        })
      }
    })
    
    onUnmounted(() => {
      // Limpiar event listeners
      websocket.off('notification-received')
      websocket.off('notification-updated')
      websocket.off('notification-stats-updated')
      websocket.off('pending-notification')
    })
    
    return {
      // Estado
      showNotifications,
      notifications,
      unreadCount,
      connectionStatus,
      
      // Métodos
      getConnectionText,
      getNotificationClass,
      getNotificationIcon,
      formatTime,
      handleNotificationClick,
      markAsRead,
      markAllAsRead,
      viewAllNotifications
    }
  }
}
</script>

<style scoped>
.realtime-notifications {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.connection-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.connection-indicator.connected {
  background: #d1fae5;
  color: #065f46;
}

.connection-indicator.connecting {
  background: #fef3c7;
  color: #92400e;
}

.connection-indicator.error {
  background: #fee2e2;
  color: #991b1b;
}

.connection-indicator.disconnected {
  background: #f3f4f6;
  color: #6b7280;
}

.indicator-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

.notification-badge {
  position: relative;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.5rem;
  background: #f3f4f6;
  color: #374151;
  transition: all 0.2s;
}

.notification-badge:hover {
  background: #e5e7eb;
}

.badge-count {
  position: absolute;
  top: -0.25rem;
  right: -0.25rem;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.notifications-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 20rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 24rem;
  overflow: hidden;
}

.dropdown-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dropdown-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.notifications-list {
  max-height: 16rem;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background: #f8fafc;
}

.notification-item.unread {
  background: #f0f9ff;
  border-left: 3px solid #3b82f6;
}

.notification-icon {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.notification-info {
  background: #dbeafe;
  color: #1e40af;
}

.notification-warning {
  background: #fef3c7;
  color: #92400e;
}

.notification-error {
  background: #fee2e2;
  color: #991b1b;
}

.notification-success {
  background: #d1fae5;
  color: #065f46;
}

.notification-alert {
  background: #fef3c7;
  color: #92400e;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.notification-message {
  color: #6b7280;
  font-size: 0.8125rem;
  line-height: 1.4;
  margin-bottom: 0.25rem;
}

.notification-time {
  color: #9ca3af;
  font-size: 0.75rem;
}

.notification-actions {
  display: flex;
  gap: 0.25rem;
}

.no-notifications {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
}

.no-notifications i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
}

.dropdown-footer {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.notifications-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 999;
}

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border: 1px solid transparent;
  gap: 0.25rem;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn-outline {
  background-color: transparent;
  color: #374151;
  border-color: #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
  border-color: #2563eb;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .notifications-dropdown {
    width: 18rem;
    right: -1rem;
  }
  
  .notification-item {
    padding: 0.5rem 0.75rem;
  }
  
  .notification-icon {
    width: 1.75rem;
    height: 1.75rem;
    font-size: 0.75rem;
  }
}
</style>

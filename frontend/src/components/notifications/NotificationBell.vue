<template>
  <div class="notification-bell">
    <!-- Bell Icon with Badge -->
    <div class="bell-container" @click="toggleDropdown">
      <i class="fas fa-bell"></i>
      <div v-if="unreadCount > 0" class="notification-badge">
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </div>
      <div v-if="hasNewNotifications" class="pulse-indicator"></div>
    </div>

    <!-- Dropdown Menu -->
    <div v-if="showDropdown" class="notification-dropdown" @click.stop>
      <div class="dropdown-header">
        <h4>
          <i class="fas fa-bell"></i>
          Notificaciones
        </h4>
        <div class="header-actions">
          <button 
            v-if="unreadCount > 0"
            class="btn btn-sm btn-outline-primary"
            @click="markAllAsRead"
          >
            <i class="fas fa-check-double"></i>
            Marcar todas
          </button>
          <button 
            class="btn btn-sm btn-outline-secondary"
            @click="goToNotificationCenter"
          >
            <i class="fas fa-external-link-alt"></i>
            Ver todas
          </button>
        </div>
      </div>

      <div class="dropdown-content">
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Cargando...</p>
        </div>

        <div v-else-if="recentNotifications.length === 0" class="empty-state">
          <i class="fas fa-bell-slash"></i>
          <p>No hay notificaciones</p>
        </div>

        <div v-else class="notifications-list">
          <div 
            v-for="notification in recentNotifications" 
            :key="notification.id"
            class="notification-item"
            :class="{ 'unread': !notification.leida }"
            @click="handleNotificationClick(notification)"
          >
            <div class="notification-icon">
              <i :class="getNotificationIcon(notification.tipo)"></i>
            </div>
            
            <div class="notification-content">
              <div class="notification-header">
                <h5 class="notification-title">{{ notification.titulo }}</h5>
                <span class="notification-time">{{ formatTime(notification.fecha_creacion) }}</span>
              </div>
              
              <p class="notification-message">{{ truncateMessage(notification.mensaje) }}</p>
            </div>
            
            <div v-if="!notification.leida" class="unread-indicator"></div>
          </div>
        </div>
      </div>

      <div class="dropdown-footer">
        <button 
          class="btn btn-sm btn-primary btn-block"
          @click="goToNotificationCenter"
        >
          <i class="fas fa-bell"></i>
          Ver todas las notificaciones
        </button>
      </div>
    </div>

    <!-- Toast Notifications -->
    <div v-if="toastNotification" class="toast-notification" :class="getToastClass(toastNotification.tipo)">
      <div class="toast-content">
        <div class="toast-icon">
          <i :class="getNotificationIcon(toastNotification.tipo)"></i>
        </div>
        <div class="toast-body">
          <h6 class="toast-title">{{ toastNotification.titulo }}</h6>
          <p class="toast-message">{{ toastNotification.mensaje }}</p>
        </div>
        <button class="toast-close" @click="closeToast">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/stores/notifications'

export default {
  name: 'NotificationBell',
  setup() {
    const router = useRouter()
    const notificationStore = useNotificationStore()

    // Reactive data
    const showDropdown = ref(false)
    const loading = ref(false)
    const recentNotifications = ref([])
    const toastNotification = ref(null)
    const hasNewNotifications = ref(false)

    // Computed
    const unreadCount = computed(() => 
      recentNotifications.value.filter(n => !n.leida).length
    )

    // Methods
    const loadRecentNotifications = async () => {
      loading.value = true
      try {
        const response = await notificationStore.getNotifications({
          page: 1,
          page_size: 5,
          ordering: '-fecha_creacion'
        })
        recentNotifications.value = response.data.results || []
      } catch (error) {
        } finally {
        loading.value = false
      }
    }

    const toggleDropdown = () => {
      showDropdown.value = !showDropdown.value
      if (showDropdown.value) {
        loadRecentNotifications()
      }
    }

    const markAllAsRead = async () => {
      try {
        await notificationStore.markAllAsRead()
        
        // Update local state
        for (const notification of recentNotifications.value) {
          if (!notification.leida) {
            notification.leida = true
            notification.fecha_lectura = new Date().toISOString()
          }
        }
        
      } catch (error) {
        }
    }

    const handleNotificationClick = async (notification) => {
      // Mark as read if not already read
      if (!notification.leida) {
        try {
          await notificationStore.markAsRead(notification.id)
          notification.leida = true
          notification.fecha_lectura = new Date().toISOString()
        } catch (error) {
          }
      }

      // Handle navigation based on notification type
      handleNotificationNavigation(notification)
      
      // Close dropdown
      showDropdown.value = false
    }

    const handleNotificationNavigation = (notification) => {
      const { tipo, datos_extra } = notification

      switch (tipo) {
        case 'report_ready':
          router.push('/admin/reports')
          break
        case 'defect_alert':
          if (datos_extra?.imagen_id) {
            router.push(`/analysis/${datos_extra.imagen_id}`)
          } else {
            router.push('/analysis')
          }
          break
        case 'training_complete':
          router.push('/admin/training')
          break
        case 'welcome':
          router.push('/profile')
          break
        default:
          router.push('/notifications')
      }
    }

    const goToNotificationCenter = () => {
      router.push('/notifications')
      showDropdown.value = false
    }

    const getNotificationIcon = (type) => {
      const icons = {
        'info': 'fas fa-info-circle',
        'success': 'fas fa-check-circle',
        'warning': 'fas fa-exclamation-triangle',
        'error': 'fas fa-times-circle',
        'defect_alert': 'fas fa-exclamation-circle',
        'report_ready': 'fas fa-file-alt',
        'training_complete': 'fas fa-brain',
        'welcome': 'fas fa-hand-wave'
      }
      return icons[type] || 'fas fa-bell'
    }

    const getToastClass = (type) => {
      const classes = {
        'info': 'toast-info',
        'success': 'toast-success',
        'warning': 'toast-warning',
        'error': 'toast-error',
        'defect_alert': 'toast-warning',
        'report_ready': 'toast-success',
        'training_complete': 'toast-success',
        'welcome': 'toast-info'
      }
      return classes[type] || 'toast-info'
    }

    const formatTime = (date) => {
      const now = new Date()
      const notificationDate = new Date(date)
      const diffMs = now - notificationDate
      const diffMinutes = Math.floor(diffMs / (1000 * 60))
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

      if (diffMinutes < 1) return 'Ahora'
      if (diffMinutes < 60) return `${diffMinutes}m`
      if (diffHours < 24) return `${diffHours}h`
      if (diffDays < 7) return `${diffDays}d`
      
      return notificationDate.toLocaleDateString('es-ES', { 
        month: 'short', 
        day: 'numeric' 
      })
    }

    const truncateMessage = (message) => {
      if (!message) return ''
      if (message.length <= 60) return message
      return message.substring(0, 60) + '...'
    }

    const showToast = (notification) => {
      toastNotification.value = notification
      
      // Auto-hide after 5 seconds
      setTimeout(() => {
        closeToast()
      }, 5000)
    }

    const closeToast = () => {
      toastNotification.value = null
    }

    // WebSocket connection for real-time notifications
    const connectWebSocket = () => {
      if (notificationStore.websocket) {
        notificationStore.websocket.onmessage = (event) => {
          const data = JSON.parse(event.data)
          if (data.type === 'notification') {
            // Add to recent notifications
            recentNotifications.value.unshift(data.notification)
            
            // Show pulse animation
            hasNewNotifications.value = true
            setTimeout(() => {
              hasNewNotifications.value = false
            }, 3000)
            
            // Show toast if enabled
            if (notificationStore.settings.show_toasts) {
              showToast(data.notification)
            }
            
            // Refresh notifications with error handling
            loadRecentNotifications().catch(err => {
              })
          }
        }
      }
    }

    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (event.target && typeof event.target.closest === 'function' && !event.target.closest('.notification-bell')) {
        showDropdown.value = false
      }
    }

    // Lifecycle
    onMounted(() => {
      // Handle potential errors to prevent unhandled promise rejections
      loadRecentNotifications().catch(err => {
        })
      connectWebSocket()
      document.addEventListener('click', handleClickOutside)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      // Data
      showDropdown,
      loading,
      recentNotifications,
      toastNotification,
      hasNewNotifications,
      
      // Computed
      unreadCount,
      
      // Methods
      toggleDropdown,
      markAllAsRead,
      handleNotificationClick,
      goToNotificationCenter,
      getNotificationIcon,
      getToastClass,
      formatTime,
      truncateMessage,
      showToast,
      closeToast
    }
  }
}
</script>

<style scoped>
.notification-bell {
  position: relative;
}

.bell-container {
  position: relative;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bell-container:hover {
  background-color: rgba(52, 152, 219, 0.1);
}

.bell-container i {
  font-size: 1.2rem;
  color: #495057;
  transition: color 0.2s;
}

.bell-container:hover i {
  color: #3498db;
}

.notification-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background-color: #c0392b;
  color: #ffffff;
  font-size: 0.7rem;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  line-height: 1.2;
}

.pulse-indicator {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 8px;
  height: 8px;
  background-color: #3498db;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(52, 152, 219, 0.7);
  }
  
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 10px rgba(52, 152, 219, 0);
  }
  
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(52, 152, 219, 0);
  }
}

.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 350px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  margin-top: 8px;
  overflow: hidden;
}

.dropdown-header {
  padding: 15px;
  border-bottom: 1px solid #ecf0f1;
  background: #f8f9fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dropdown-header h4 {
  margin: 0;
  font-size: 1rem;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dropdown-header h4 i {
  color: #3498db;
}

.header-actions {
  display: flex;
  gap: 5px;
}

.dropdown-content {
  max-height: 400px;
  overflow-y: auto;
}

.loading-state,
.empty-state {
  padding: 30px;
  text-align: center;
  color: #7f8c8d;
}

.loading-state i {
  font-size: 1.5rem;
  margin-bottom: 8px;
  color: #3498db;
}

.empty-state i {
  font-size: 2rem;
  margin-bottom: 10px;
  color: #bdc3c7;
}

.notifications-list {
  padding: 0;
}

.notification-item {
  display: flex;
  padding: 12px 15px;
  border-bottom: 1px solid #ecf0f1;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.notification-item:hover {
  background-color: #f8f9fa;
}

.notification-item.unread {
  background-color: #e3f2fd;
  border-left: 3px solid #3498db;
}

.notification-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.notification-icon i {
  font-size: 1rem;
  color: #3498db;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4px;
}

.notification-title {
  margin: 0;
  font-size: 0.9rem;
  color: #2c3e50;
  font-weight: 600;
  line-height: 1.2;
}

.notification-time {
  font-size: 0.7rem;
  color: #7f8c8d;
  white-space: nowrap;
  margin-left: 8px;
}

.notification-message {
  margin: 0;
  color: #495057;
  font-size: 0.8rem;
  line-height: 1.3;
}

.unread-indicator {
  position: absolute;
  top: 50%;
  right: 8px;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  background-color: #3498db;
  border-radius: 50%;
}

.dropdown-footer {
  padding: 15px;
  border-top: 1px solid #ecf0f1;
  background: #f8f9fa;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 0.7rem;
}

.btn-block {
  width: 100%;
  justify-content: center;
}

.btn-primary {
  background-color: #1f4e79;
  color: #ffffff;
}

.btn-primary:hover {
  background-color: #1a3d5b;
}

.btn-outline-primary {
  background-color: transparent;
  color: #3498db;
  border: 1px solid #3498db;
}

.btn-outline-primary:hover {
  background-color: #1f4e79;
  color: #ffffff;
}

.btn-outline-secondary {
  background-color: transparent;
  color: #6c757d;
  border: 1px solid #6c757d;
}

.btn-outline-secondary:hover {
  background-color: #6c757d;
  color: white;
}

/* Toast Notifications */
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 350px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 2000;
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast-content {
  display: flex;
  padding: 15px;
  align-items: flex-start;
  gap: 12px;
}

.toast-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.toast-info .toast-icon {
  background-color: #d1ecf1;
  color: #0c5460;
}

.toast-success .toast-icon {
  background-color: #d4edda;
  color: #155724;
}

.toast-warning .toast-icon {
  background-color: #fff3cd;
  color: #856404;
}

.toast-error .toast-icon {
  background-color: #f8d7da;
  color: #721c24;
}

.toast-body {
  flex: 1;
}

.toast-title {
  margin: 0 0 4px 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #2c3e50;
}

.toast-message {
  margin: 0;
  font-size: 0.8rem;
  color: #495057;
  line-height: 1.3;
}

.toast-close {
  background: none;
  border: none;
  color: #7f8c8d;
  cursor: pointer;
  padding: 4px;
  border-radius: 3px;
  transition: all 0.2s;
}

.toast-close:hover {
  background-color: #f8f9fa;
  color: #2c3e50;
}

@media (max-width: 768px) {
  .notification-dropdown {
    width: 300px;
    right: -50px;
  }
  
  .toast-notification {
    width: 300px;
    right: 10px;
  }
}
</style>

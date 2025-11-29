<template>
  <div class="notification-center">
    <!-- Header -->
    <div class="notification-header">
      <div class="header-content">
        <h3>
          <i class="fas fa-bell"></i>
          Centro de Notificaciones
        </h3>
        <div class="header-actions">
          <button 
            class="btn btn-sm btn-outline-primary"
            @click="markAllAsRead"
            :disabled="unreadCount === 0"
          >
            <i class="fas fa-check-double"></i>
            Marcar Todas como Leídas
          </button>
          <button 
            class="btn btn-sm btn-outline-secondary"
            @click="refreshNotifications"
            :disabled="loading"
          >
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            Actualizar
          </button>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="notification-filters">
      <div class="filter-tabs">
        <button 
          class="filter-tab"
          :class="{ active: activeFilter === 'all' }"
          @click="setFilter('all')"
        >
          Todas ({{ totalCount }})
        </button>
        <button 
          class="filter-tab"
          :class="{ active: activeFilter === 'unread' }"
          @click="setFilter('unread')"
        >
          No Leídas ({{ unreadCount }})
        </button>
        <button 
          class="filter-tab"
          :class="{ active: activeFilter === 'read' }"
          @click="setFilter('read')"
        >
          Leídas ({{ readCount }})
        </button>
      </div>

      <div class="filter-options">
        <select v-model="typeFilter" @change="applyFilters">
          <option value="">Todos los tipos</option>
          <option value="info">Información</option>
          <option value="success">Éxito</option>
          <option value="warning">Advertencia</option>
          <option value="error">Error</option>
          <option value="defect_alert">Alerta de Defecto</option>
          <option value="report_ready">Reporte Listo</option>
          <option value="training_complete">Entrenamiento Completo</option>
          <option value="welcome">Bienvenida</option>
        </select>
      </div>
    </div>

    <!-- Lista de Notificaciones -->
    <div class="notification-list">
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Cargando notificaciones...</p>
      </div>

      <div v-else-if="filteredNotifications.length === 0" class="empty-state">
        <i class="fas fa-bell-slash"></i>
        <h3>No hay notificaciones</h3>
        <p v-if="activeFilter === 'unread'">No tienes notificaciones sin leer.</p>
        <p v-else-if="activeFilter === 'read'">No tienes notificaciones leídas.</p>
        <p v-else>No tienes notificaciones disponibles.</p>
      </div>

      <div v-else class="notifications">
        <div 
          v-for="notification in filteredNotifications" 
          :key="notification.id"
          class="notification-item"
          :class="{ 
            'unread': !notification.leida,
            'read': notification.leida
          }"
          @click="markAsRead(notification)"
        >
          <div class="notification-icon">
            <i :class="getNotificationIcon(notification.tipo)"></i>
          </div>
          
          <div class="notification-content">
            <div class="notification-header">
              <h4 class="notification-title">{{ notification.titulo }}</h4>
              <span class="notification-time">{{ formatTime(notification.fecha_creacion) }}</span>
            </div>
            
            <p class="notification-message">{{ notification.mensaje }}</p>
            
            <div v-if="notification.datos_extra && Object.keys(notification.datos_extra).length > 0" class="notification-extra">
              <div class="extra-data">
                <span v-for="(value, key) in notification.datos_extra" :key="key" class="extra-item">
                  <strong>{{ key }}:</strong> {{ value }}
                </span>
              </div>
            </div>
            
            <div class="notification-actions">
              <button 
                v-if="!notification.leida"
                class="btn btn-sm btn-outline-primary"
                @click.stop="markAsRead(notification)"
              >
                <i class="fas fa-check"></i>
                Marcar como Leída
              </button>
              <button 
                class="btn btn-sm btn-outline-danger"
                @click.stop="deleteNotification(notification)"
              >
                <i class="fas fa-trash"></i>
                Eliminar
              </button>
            </div>
          </div>
          
          <div class="notification-status">
            <div v-if="!notification.leida" class="unread-indicator"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Paginación -->
    <div v-if="totalPages > 1" class="pagination-container">
      <nav aria-label="Paginación de notificaciones">
        <ul class="pagination">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button 
              class="page-link"
              @click="changePage(currentPage - 1)"
              :disabled="currentPage === 1"
            >
              <i class="fas fa-chevron-left"></i>
            </button>
          </li>
          
          <li 
            v-for="page in visiblePages" 
            :key="page"
            class="page-item"
            :class="{ active: page === currentPage }"
          >
            <button 
              class="page-link"
              @click="changePage(page)"
            >
              {{ page }}
            </button>
          </li>
          
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <button 
              class="page-link"
              @click="changePage(currentPage + 1)"
              :disabled="currentPage === totalPages"
            >
              <i class="fas fa-chevron-right"></i>
            </button>
          </li>
        </ul>
      </nav>
    </div>

    <!-- Configuración de Notificaciones -->
    <div class="notification-settings">
      <h4>
        <i class="fas fa-cog"></i>
        Configuración de Notificaciones
      </h4>
      
      <div class="settings-grid">
        <div class="setting-item">
          <label class="setting-label">
            <input 
              type="checkbox" 
              v-model="settings.email_notifications"
              @change="updateSettings"
            >
            <span class="checkmark"></span>
            Notificaciones por Email
          </label>
        </div>
        
        <div class="setting-item">
          <label class="setting-label">
            <input 
              type="checkbox" 
              v-model="settings.push_notifications"
              @change="updateSettings"
            >
            <span class="checkmark"></span>
            Notificaciones Push
          </label>
        </div>
        
        <div class="setting-item">
          <label class="setting-label">
            <input 
              type="checkbox" 
              v-model="settings.report_notifications"
              @change="updateSettings"
            >
            <span class="checkmark"></span>
            Notificaciones de Reportes
          </label>
        </div>
        
        <div class="setting-item">
          <label class="setting-label">
            <input 
              type="checkbox" 
              v-model="settings.analysis_notifications"
              @change="updateSettings"
            >
            <span class="checkmark"></span>
            Notificaciones de Análisis
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useNotificationStore } from '@/stores/notifications'
import Swal from 'sweetalert2'

export default {
  name: 'NotificationCenter',
  setup() {
    const notificationStore = useNotificationStore()

    // Reactive data
    const loading = ref(false)
    const notifications = ref([])
    const activeFilter = ref('all')
    const typeFilter = ref('')
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalCount = ref(0)
    const totalPages = ref(0)

    const settings = ref({
      email_notifications: true,
      push_notifications: true,
      report_notifications: true,
      analysis_notifications: true
    })

    // Computed
    const unreadCount = computed(() => 
      notifications.value.filter(n => !n.leida).length
    )
    
    const readCount = computed(() => 
      notifications.value.filter(n => n.leida).length
    )
    
    const filteredNotifications = computed(() => {
      let filtered = notifications.value

      // Filter by read status
      if (activeFilter.value === 'unread') {
        filtered = filtered.filter(n => !n.leida)
      } else if (activeFilter.value === 'read') {
        filtered = filtered.filter(n => n.leida)
      }

      // Filter by type
      if (typeFilter.value) {
        filtered = filtered.filter(n => n.tipo === typeFilter.value)
      }

      return filtered
    })
    
    const visiblePages = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, start + 4)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    // Methods
    const loadNotifications = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          page_size: pageSize.value
        }
        
        const response = await notificationStore.getNotifications(params)
        notifications.value = response.data.results || []
        totalCount.value = response.data.count || 0
        totalPages.value = Math.ceil(totalCount.value / pageSize.value)
        
      } catch (error) {
        console.error('Error loading notifications:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron cargar las notificaciones'
        })
      } finally {
        loading.value = false
      }
    }

    const refreshNotifications = () => {
      loadNotifications()
    }

    const setFilter = (filter) => {
      activeFilter.value = filter
      currentPage.value = 1
    }

    const applyFilters = () => {
      currentPage.value = 1
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadNotifications()
      }
    }

    const markAsRead = async (notification) => {
      if (notification.leida) return

      try {
        await notificationStore.markAsRead(notification.id)
        
        // Update local state
        const index = notifications.value.findIndex(n => n.id === notification.id)
        if (index !== -1) {
          notifications.value[index].leida = true
          notifications.value[index].fecha_lectura = new Date().toISOString()
        }
        
      } catch (error) {
        console.error('Error marking notification as read:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo marcar la notificación como leída'
        })
      }
    }

    const markAllAsRead = async () => {
      try {
        await notificationStore.markAllAsRead()
        
        // Update local state
        for (const notification of notifications.value) {
          if (!notification.leida) {
            notification.leida = true
            notification.fecha_lectura = new Date().toISOString()
          }
        }
        
        Swal.fire({
          icon: 'success',
          title: 'Notificaciones marcadas',
          text: 'Todas las notificaciones han sido marcadas como leídas'
        })
        
      } catch (error) {
        console.error('Error marking all notifications as read:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron marcar todas las notificaciones como leídas'
        })
      }
    }

    const deleteNotification = async (notification) => {
      const result = await Swal.fire({
        title: '¿Eliminar notificación?',
        text: 'Esta acción no se puede deshacer.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      })

      if (result.isConfirmed) {
        try {
          await notificationStore.deleteNotification(notification.id)
          
          // Remove from local state
          notifications.value = notifications.value.filter(n => n.id !== notification.id)
          totalCount.value--
          
          Swal.fire({
            icon: 'success',
            title: 'Notificación eliminada',
            text: 'La notificación ha sido eliminada exitosamente'
          })
          
        } catch (error) {
          console.error('Error deleting notification:', error)
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudo eliminar la notificación'
          })
        }
      }
    }

    const updateSettings = async () => {
      try {
        await notificationStore.updateSettings(settings.value)
        
        Swal.fire({
          icon: 'success',
          title: 'Configuración actualizada',
          text: 'Las preferencias de notificaciones han sido guardadas'
        })
        
      } catch (error) {
        console.error('Error updating notification settings:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron actualizar las preferencias'
        })
      }
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

    const formatTime = (date) => {
      const now = new Date()
      const notificationDate = new Date(date)
      const diffMs = now - notificationDate
      const diffMinutes = Math.floor(diffMs / (1000 * 60))
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

      if (diffMinutes < 1) return 'Ahora mismo'
      if (diffMinutes < 60) return `Hace ${diffMinutes} min`
      if (diffHours < 24) return `Hace ${diffHours} h`
      if (diffDays < 7) return `Hace ${diffDays} días`
      
      return notificationDate.toLocaleDateString('es-ES')
    }

    // WebSocket connection for real-time notifications
    const connectWebSocket = () => {
      if (notificationStore.websocket) {
        notificationStore.websocket.onmessage = (event) => {
          const data = JSON.parse(event.data)
          if (data.type === 'notification') {
            // Add new notification to the list
            notifications.value.unshift(data.notification)
            totalCount.value++
            
            // Show toast notification
            notificationStore.showToast(data.notification)
          }
        }
      }
    }

    // Lifecycle
    onMounted(() => {
      loadNotifications()
      connectWebSocket()
    })

    onUnmounted(() => {
      // Cleanup WebSocket connection if needed
    })

    return {
      // Data
      loading,
      notifications,
      activeFilter,
      typeFilter,
      currentPage,
      totalCount,
      totalPages,
      settings,
      
      // Computed
      unreadCount,
      readCount,
      filteredNotifications,
      visiblePages,
      
      // Methods
      loadNotifications,
      refreshNotifications,
      setFilter,
      applyFilters,
      changePage,
      markAsRead,
      markAllAsRead,
      deleteNotification,
      updateSettings,
      getNotificationIcon,
      formatTime
    }
  }
}
</script>

<style scoped>
.notification-center {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.notification-header {
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
  background: #f8f9fa;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 5px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notification-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.notification-header h3 i {
  margin-right: 10px;
  color: #3498db;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.notification-filters {
  padding: 15px 20px;
  border-bottom: 1px solid #ecf0f1;
  background: #f8f9fa;
}

.filter-tabs {
  display: flex;
  gap: 5px;
  margin-bottom: 15px;
}

.filter-tab {
  padding: 8px 16px;
  border: 1px solid #dee2e6;
  background: white;
  color: #495057;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.filter-tab:hover {
  background-color: #e9ecef;
  color: #212529;
}

.filter-tab.active {
  background-color: #1f4e79;
  color: #ffffff;
  border-color: #1f4e79;
}

.filter-options select {
  padding: 8px 12px;
  border: 1px solid #dee2e6;
  border-radius: 5px;
  font-size: 0.9rem;
  background: white;
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.loading-state,
.empty-state {
  padding: 40px;
  text-align: center;
  color: #7f8c8d;
}

.loading-state i {
  font-size: 2rem;
  margin-bottom: 10px;
  color: #3498db;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 15px;
  color: #bdc3c7;
}

.notifications {
  padding: 0;
}

.notification-item {
  display: flex;
  padding: 15px 20px;
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
  border-left: 4px solid #3498db;
}

.notification-item.read {
  opacity: 0.8;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}

.notification-icon i {
  font-size: 1.2rem;
  color: #3498db;
}

.notification-content {
  flex: 1;
}


.notification-title {
  margin: 0;
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 600;
}

.notification-time {
  font-size: 0.8rem;
  color: #7f8c8d;
  white-space: nowrap;
}

.notification-message {
  margin: 0 0 10px 0;
  color: #495057;
  line-height: 1.4;
}

.notification-extra {
  margin-bottom: 10px;
}

.extra-data {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.extra-item {
  font-size: 0.8rem;
  color: #495057;
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
}

.notification-actions {
  display: flex;
  gap: 8px;
}

.notification-status {
  display: flex;
  align-items: center;
  margin-left: 10px;
}

.unread-indicator {
  width: 8px;
  height: 8px;
  background-color: #3498db;
  border-radius: 50%;
}

.pagination-container {
  padding: 20px;
  display: flex;
  justify-content: center;
  border-top: 1px solid #ecf0f1;
}

.pagination {
  margin: 0;
}

.page-item.active .page-link {
  background-color: #3498db;
  border-color: #3498db;
}

.page-link {
  color: #3498db;
  border-color: #dee2e6;
}

.page-link:hover {
  color: #1e5a8a;
  background-color: #e9ecef;
  border-color: #dee2e6;
}

.notification-settings {
  padding: 20px;
  border-top: 1px solid #ecf0f1;
  background: #f8f9fa;
}

.notification-settings h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.notification-settings h4 i {
  color: #3498db;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.setting-item {
  display: flex;
  align-items: center;
}

.setting-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.9rem;
  color: #495057;
  gap: 8px;
}

.setting-label input[type="checkbox"] {
  margin: 0;
  width: auto;
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

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline-primary {
  background-color: transparent;
  color: #3498db;
  border: 1px solid #3498db;
}

.btn-outline-primary:hover:not(:disabled) {
  background-color: #1f4e79;
  color: #ffffff;
}

.btn-outline-secondary {
  background-color: transparent;
  color: #6c757d;
  border: 1px solid #6c757d;
}

.btn-outline-secondary:hover:not(:disabled) {
  background-color: #6c757d;
  color: white;
}

.btn-outline-danger {
  background-color: transparent;
  color: #dc3545;
  border: 1px solid #dc3545;
}

.btn-outline-danger:hover:not(:disabled) {
  background-color: #dc3545;
  color: white;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .filter-tabs {
    flex-wrap: wrap;
  }
  
  .notification-header {
    flex-direction: column;
    gap: 5px;
  }
  
  .notification-actions {
    flex-direction: column;
  }
  
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>

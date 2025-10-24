<template>
  <div class="system-status-widget">
    <div class="widget-header">
      <h3>
        <i class="fas fa-server"></i>
        Estado del Sistema
      </h3>
      <div class="connection-status" :class="connectionStatus">
        <div class="status-dot"></div>
        <span>{{ getConnectionText() }}</span>
      </div>
    </div>

    <div v-if="systemStatus" class="status-content">
      <!-- Estado general -->
      <div class="status-section">
        <div class="status-item">
          <span class="status-label">Estado:</span>
          <span class="status-value" :class="getStatusClass(systemStatus.system_status)">
            <i :class="getStatusIcon(systemStatus.system_status)"></i>
            {{ getStatusText(systemStatus.system_status) }}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">Última actualización:</span>
          <span class="status-value">{{ formatTime(systemStatus.timestamp) }}</span>
        </div>
      </div>

      <!-- Estadísticas de usuarios -->
      <div class="status-section">
        <h4>Usuarios</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ systemStatus.users?.total || 0 }}</div>
            <div class="stat-label">Total</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ systemStatus.users?.active || 0 }}</div>
            <div class="stat-label">Activos</div>
          </div>
        </div>
      </div>

      <!-- Estadísticas de notificaciones -->
      <div class="status-section">
        <h4>Notificaciones</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ systemStatus.notifications?.total || 0 }}</div>
            <div class="stat-label">Total</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ systemStatus.notifications?.unread || 0 }}</div>
            <div class="stat-label">No leídas</div>
          </div>
        </div>
      </div>

      <!-- Estadísticas de actividad -->
      <div class="status-section">
        <h4>Actividad Hoy</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ systemStatus.activity?.today_activities || 0 }}</div>
            <div class="stat-label">Actividades</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ systemStatus.activity?.today_logins || 0 }}</div>
            <div class="stat-label">Logins</div>
          </div>
        </div>
      </div>

      <!-- Conexiones WebSocket -->
      <div class="status-section">
        <h4>Conexiones WebSocket</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ systemStatus.websocket_connections?.notifications || 0 }}</div>
            <div class="stat-label">Notificaciones</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ systemStatus.websocket_connections?.system_status || 0 }}</div>
            <div class="stat-label">Estado</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ systemStatus.websocket_connections?.audit || 0 }}</div>
            <div class="stat-label">Auditoría</div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="loading-state">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
      </div>
      <p>Cargando estado del sistema...</p>
    </div>

    <!-- Alertas del sistema -->
    <div v-if="systemAlerts.length > 0" class="alerts-section">
      <h4>
        <i class="fas fa-exclamation-triangle"></i>
        Alertas del Sistema
      </h4>
      <div class="alerts-list">
        <div
          v-for="alert in systemAlerts"
          :key="alert.id"
          class="alert-item"
          :class="getAlertClass(alert.level)"
        >
          <div class="alert-icon">
            <i :class="getAlertIcon(alert.level)"></i>
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-message">{{ alert.message }}</div>
            <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
          </div>
          <button
            @click="dismissAlert(alert.id)"
            class="alert-dismiss"
            title="Descartar alerta"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Acciones -->
    <div class="widget-actions">
      <button
        @click="refreshStatus"
        class="btn btn-sm btn-outline"
        :disabled="isRefreshing"
      >
        <i class="fas fa-sync-alt" :class="{ 'fa-spin': isRefreshing }"></i>
        Actualizar
      </button>
      <button
        @click="toggleAutoRefresh"
        class="btn btn-sm"
        :class="autoRefresh ? 'btn-success' : 'btn-outline'"
      >
        <i class="fas fa-play" v-if="!autoRefresh"></i>
        <i class="fas fa-pause" v-else></i>
        {{ autoRefresh ? 'Auto-actualizar ON' : 'Auto-actualizar OFF' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWebSocket } from '@/composables/useWebSocket'

export default {
  name: 'SystemStatusWidget',
  setup() {
    const websocket = useWebSocket()
    
    // Estado reactivo
    const systemStatus = ref(null)
    const systemAlerts = ref([])
    const isRefreshing = ref(false)
    const autoRefresh = ref(true)
    const refreshInterval = ref(null)
    
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
          return 'Error'
        default:
          return 'Desconectado'
      }
    }
    
    const getStatusClass = (status) => {
      switch (status) {
        case 'online':
          return 'status-online'
        case 'warning':
          return 'status-warning'
        case 'error':
          return 'status-error'
        default:
          return 'status-unknown'
      }
    }
    
    const getStatusIcon = (status) => {
      switch (status) {
        case 'online':
          return 'fas fa-check-circle'
        case 'warning':
          return 'fas fa-exclamation-triangle'
        case 'error':
          return 'fas fa-times-circle'
        default:
          return 'fas fa-question-circle'
      }
    }
    
    const getStatusText = (status) => {
      switch (status) {
        case 'online':
          return 'En línea'
        case 'warning':
          return 'Advertencia'
        case 'error':
          return 'Error'
        default:
          return 'Desconocido'
      }
    }
    
    const getAlertClass = (level) => {
      switch (level) {
        case 'info':
          return 'alert-info'
        case 'warning':
          return 'alert-warning'
        case 'error':
          return 'alert-error'
        case 'critical':
          return 'alert-critical'
        default:
          return 'alert-info'
      }
    }
    
    const getAlertIcon = (level) => {
      switch (level) {
        case 'info':
          return 'fas fa-info-circle'
        case 'warning':
          return 'fas fa-exclamation-triangle'
        case 'error':
          return 'fas fa-times-circle'
        case 'critical':
          return 'fas fa-skull-crossbones'
        default:
          return 'fas fa-bell'
      }
    }
    
    const formatTime = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString('es-ES', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
    
    const refreshStatus = async () => {
      isRefreshing.value = true
      try {
        websocket.getSystemStatus()
      } finally {
        setTimeout(() => {
          isRefreshing.value = false
        }, 1000)
      }
    }
    
    const toggleAutoRefresh = () => {
      autoRefresh.value = !autoRefresh.value
      
      if (autoRefresh.value) {
        startAutoRefresh()
      } else {
        stopAutoRefresh()
      }
    }
    
    const startAutoRefresh = () => {
      refreshInterval.value = setInterval(() => {
        websocket.getSystemStatus()
      }, 30000) // Cada 30 segundos
    }
    
    const stopAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
    }
    
    const dismissAlert = (alertId) => {
      systemAlerts.value = systemAlerts.value.filter(alert => alert.id !== alertId)
    }
    
    const handleSystemStatusUpdate = (data) => {
      systemStatus.value = data
    }
    
    const handleSystemAlert = (data) => {
      const alert = {
        id: Date.now(),
        ...data,
        timestamp: new Date().toISOString()
      }
      
      systemAlerts.value.unshift(alert)
      
      // Limitar a 5 alertas
      if (systemAlerts.value.length > 5) {
        systemAlerts.value = systemAlerts.value.slice(0, 5)
      }
      
      // Mostrar notificación
      if (data.level === 'critical' || data.level === 'error') {
        // Mostrar alerta crítica
        console.error('Alerta crítica del sistema:', data)
      }
    }
    
    // Lifecycle
    onMounted(() => {
      // Configurar event listeners
      websocket.on('system-status-updated', handleSystemStatusUpdate)
      websocket.on('system-alert', handleSystemAlert)
      
      // Obtener estado inicial
      refreshStatus()
      
      // Iniciar auto-actualización
      if (autoRefresh.value) {
        startAutoRefresh()
      }
    })
    
    onUnmounted(() => {
      // Limpiar event listeners
      websocket.off('system-status-updated', handleSystemStatusUpdate)
      websocket.off('system-alert', handleSystemAlert)
      
      // Detener auto-actualización
      stopAutoRefresh()
    })
    
    return {
      // Estado
      systemStatus,
      systemAlerts,
      isRefreshing,
      autoRefresh,
      connectionStatus,
      
      // Métodos
      getConnectionText,
      getStatusClass,
      getStatusIcon,
      getStatusText,
      getAlertClass,
      getAlertIcon,
      formatTime,
      refreshStatus,
      toggleAutoRefresh,
      dismissAlert
    }
  }
}
</script>

<style scoped>
.system-status-widget {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.widget-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.connection-status.connected {
  background: #d1fae5;
  color: #065f46;
}

.connection-status.connecting {
  background: #fef3c7;
  color: #92400e;
}

.connection-status.error {
  background: #fee2e2;
  color: #991b1b;
}

.connection-status.disconnected {
  background: #f3f4f6;
  color: #6b7280;
}

.status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: currentColor;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.status-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.status-section h4 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.status-label {
  color: #6b7280;
  font-size: 0.875rem;
}

.status-value {
  font-weight: 500;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.status-online {
  color: #059669;
}

.status-warning {
  color: #d97706;
}

.status-error {
  color: #dc2626;
}

.status-unknown {
  color: #6b7280;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #6b7280;
}

.loading-spinner {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: #3b82f6;
}

.alerts-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.alerts-section h4 {
  margin: 0 0 1rem 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid;
}

.alert-info {
  background: #f0f9ff;
  border-color: #bae6fd;
}

.alert-warning {
  background: #fef3c7;
  border-color: #fde68a;
}

.alert-error {
  background: #fee2e2;
  border-color: #fecaca;
}

.alert-critical {
  background: #fef2f2;
  border-color: #fecaca;
  border-width: 2px;
}

.alert-icon {
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-title {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.alert-message {
  color: #6b7280;
  font-size: 0.8125rem;
  line-height: 1.4;
  margin-bottom: 0.25rem;
}

.alert-time {
  color: #9ca3af;
  font-size: 0.75rem;
}

.alert-dismiss {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.alert-dismiss:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #374151;
}

.widget-actions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border: 1px solid transparent;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
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

.btn-success {
  background-color: #10b981;
  color: white;
  border-color: #10b981;
}

.btn-success:hover:not(:disabled) {
  background-color: #059669;
  border-color: #059669;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .system-status-widget {
    padding: 1rem;
  }
  
  .widget-header {
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .widget-actions {
    flex-direction: column;
  }
}
</style>

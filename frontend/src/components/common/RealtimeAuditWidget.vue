<template>
  <div class="realtime-audit-widget">
    <div class="widget-header">
      <h3>
        <i class="fas fa-shield-alt"></i>
        Auditoría en Tiempo Real
      </h3>
      <div class="connection-status" :class="connectionStatus">
        <div class="status-dot"></div>
        <span>{{ getConnectionText() }}</span>
      </div>
    </div>

    <!-- Estadísticas de auditoría -->
    <div v-if="auditStats" class="audit-stats">
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ auditStats.activities?.total || 0 }}</div>
          <div class="stat-label">Actividades Totales</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ auditStats.activities?.today || 0 }}</div>
          <div class="stat-label">Hoy</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ auditStats.logins?.total || 0 }}</div>
          <div class="stat-label">Logins Totales</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ Math.round(auditStats.logins?.success_rate || 0) }}%</div>
          <div class="stat-label">Tasa de Éxito</div>
        </div>
      </div>
    </div>

    <!-- Actividad reciente -->
    <div class="recent-activity">
      <div class="section-header">
        <h4>Actividad Reciente</h4>
        <div class="header-actions">
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

      <div class="activity-list">
        <div
          v-for="activity in recentActivities"
          :key="activity.id"
          class="activity-item"
          :class="getActivityClass(activity.accion)"
        >
          <div class="activity-icon">
            <i :class="getActivityIcon(activity.accion)"></i>
          </div>
          
          <div class="activity-content">
            <div class="activity-header">
              <span class="activity-user">{{ activity.usuario }}</span>
              <span class="activity-action">{{ activity.accion_display }}</span>
              <span class="activity-model">{{ activity.modelo }}</span>
            </div>
            <div class="activity-description">{{ activity.descripcion }}</div>
            <div class="activity-meta">
              <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
              <span class="activity-ip">{{ activity.ip_address }}</span>
            </div>
          </div>
        </div>

        <div v-if="recentActivities.length === 0" class="no-activity">
          <i class="fas fa-history"></i>
          <p>No hay actividad reciente</p>
        </div>
      </div>
    </div>

    <!-- Logins recientes -->
    <div class="recent-logins">
      <div class="section-header">
        <h4>Logins Recientes</h4>
      </div>

      <div class="logins-list">
        <div
          v-for="login in recentLogins"
          :key="login.id"
          class="login-item"
          :class="login.success ? 'login-success' : 'login-failed'"
        >
          <div class="login-icon">
            <i :class="login.success ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
          </div>
          
          <div class="login-content">
            <div class="login-header">
              <span class="login-user">{{ login.usuario }}</span>
              <span class="login-status">{{ login.success ? 'Exitoso' : 'Fallido' }}</span>
            </div>
            <div class="login-meta">
              <span class="login-time">{{ formatTime(login.login_time) }}</span>
              <span class="login-ip">{{ login.ip_address }}</span>
              <span v-if="login.failure_reason" class="login-error">{{ login.failure_reason }}</span>
            </div>
          </div>
        </div>

        <div v-if="recentLogins.length === 0" class="no-logins">
          <i class="fas fa-sign-in-alt"></i>
          <p>No hay logins recientes</p>
        </div>
      </div>
    </div>

    <!-- Acciones -->
    <div class="widget-actions">
      <button
        @click="refreshAuditData"
        class="btn btn-sm btn-outline"
        :disabled="isRefreshing"
      >
        <i class="fas fa-sync-alt" :class="{ 'fa-spin': isRefreshing }"></i>
        Actualizar
      </button>
      <button
        @click="viewFullAudit"
        class="btn btn-sm btn-primary"
      >
        <i class="fas fa-external-link-alt"></i>
        Ver Auditoría Completa
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWebSocket } from '@/composables/useWebSocket'

export default {
  name: 'RealtimeAuditWidget',
  setup() {
    const router = useRouter()
    const websocket = useWebSocket()
    
    // Estado reactivo
    const auditStats = ref(null)
    const recentActivities = ref([])
    const recentLogins = ref([])
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
    
    const getActivityClass = (action) => {
      const classes = {
        'login': 'activity-login',
        'logout': 'activity-logout',
        'create': 'activity-create',
        'update': 'activity-update',
        'delete': 'activity-delete',
        'view': 'activity-view',
        'download': 'activity-download',
        'upload': 'activity-upload',
        'analysis': 'activity-analysis',
        'training': 'activity-training',
        'report': 'activity-report',
        'error': 'activity-error'
      }
      return classes[action] || 'activity-default'
    }
    
    const getActivityIcon = (action) => {
      const icons = {
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
      return icons[action] || 'fas fa-circle'
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
    
    const refreshAuditData = async () => {
      isRefreshing.value = true
      try {
        websocket.getAuditStats()
        websocket.getRecentActivity()
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
        websocket.getAuditStats()
        websocket.getRecentActivity()
      }, 30000) // Cada 30 segundos
    }
    
    const stopAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
    }
    
    const viewFullAudit = () => {
      router.push('/auditoria')
    }
    
    const handleAuditStatsUpdate = (data) => {
      auditStats.value = data
    }
    
    const handleRecentActivity = (data) => {
      recentActivities.value = data.activities || []
      recentLogins.value = data.logins || []
    }
    
    const handleAuditActivity = (data) => {
      // Agregar nueva actividad al inicio
      recentActivities.value.unshift(data)
      
      // Limitar a 20 actividades
      if (recentActivities.value.length > 20) {
        recentActivities.value = recentActivities.value.slice(0, 20)
      }
    }
    
    const handleAuditLogin = (data) => {
      // Agregar nuevo login al inicio
      recentLogins.value.unshift(data)
      
      // Limitar a 10 logins
      if (recentLogins.value.length > 10) {
        recentLogins.value = recentLogins.value.slice(0, 10)
      }
    }
    
    // Lifecycle
    onMounted(() => {
      // Configurar event listeners
      websocket.on('audit-stats-updated', handleAuditStatsUpdate)
      websocket.on('recent-activity', handleRecentActivity)
      websocket.on('audit-activity', handleAuditActivity)
      websocket.on('audit-login', handleAuditLogin)
      
      // Obtener datos iniciales
      refreshAuditData()
      
      // Iniciar auto-actualización
      if (autoRefresh.value) {
        startAutoRefresh()
      }
    })
    
    onUnmounted(() => {
      // Limpiar event listeners
      websocket.off('audit-stats-updated', handleAuditStatsUpdate)
      websocket.off('recent-activity', handleRecentActivity)
      websocket.off('audit-activity', handleAuditActivity)
      websocket.off('audit-login', handleAuditLogin)
      
      // Detener auto-actualización
      stopAutoRefresh()
    })
    
    return {
      // Estado
      auditStats,
      recentActivities,
      recentLogins,
      isRefreshing,
      autoRefresh,
      connectionStatus,
      
      // Métodos
      getConnectionText,
      getActivityClass,
      getActivityIcon,
      formatTime,
      refreshAuditData,
      toggleAutoRefresh,
      viewFullAudit
    }
  }
}
</script>

<style scoped>
.realtime-audit-widget {
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

.audit-stats {
  margin-bottom: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h4 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.activity-list,
.logins-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.activity-item:hover {
  background: #f8fafc;
}

.activity-login {
  border-left: 3px solid #3b82f6;
}

.activity-logout {
  border-left: 3px solid #f59e0b;
}

.activity-create {
  border-left: 3px solid #10b981;
}

.activity-update {
  border-left: 3px solid #3b82f6;
}

.activity-delete {
  border-left: 3px solid #ef4444;
}

.activity-view {
  border-left: 3px solid #8b5cf6;
}

.activity-download {
  border-left: 3px solid #059669;
}

.activity-upload {
  border-left: 3px solid #0284c7;
}

.activity-analysis {
  border-left: 3px solid #f59e0b;
}

.activity-training {
  border-left: 3px solid #8b5cf6;
}

.activity-report {
  border-left: 3px solid #059669;
}

.activity-error {
  border-left: 3px solid #ef4444;
}

.activity-default {
  border-left: 3px solid #6b7280;
}

.activity-icon {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.activity-login .activity-icon {
  background: #dbeafe;
  color: #1e40af;
}

.activity-logout .activity-icon {
  background: #fef3c7;
  color: #92400e;
}

.activity-create .activity-icon {
  background: #d1fae5;
  color: #065f46;
}

.activity-update .activity-icon {
  background: #dbeafe;
  color: #1e40af;
}

.activity-delete .activity-icon {
  background: #fee2e2;
  color: #991b1b;
}

.activity-view .activity-icon {
  background: #f3e8ff;
  color: #7c3aed;
}

.activity-download .activity-icon {
  background: #ecfdf5;
  color: #047857;
}

.activity-upload .activity-icon {
  background: #f0f9ff;
  color: #0369a1;
}

.activity-analysis .activity-icon {
  background: #fef3c7;
  color: #92400e;
}

.activity-training .activity-icon {
  background: #f3e8ff;
  color: #7c3aed;
}

.activity-report .activity-icon {
  background: #ecfdf5;
  color: #047857;
}

.activity-error .activity-icon {
  background: #fee2e2;
  color: #991b1b;
}

.activity-default .activity-icon {
  background: #f3f4f6;
  color: #374151;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-header {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.25rem;
  flex-wrap: wrap;
}

.activity-user {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.875rem;
}

.activity-action {
  background: #f3f4f6;
  color: #374151;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.activity-model {
  color: #6b7280;
  font-size: 0.75rem;
  font-style: italic;
}

.activity-description {
  color: #6b7280;
  font-size: 0.8125rem;
  line-height: 1.4;
  margin-bottom: 0.25rem;
}

.activity-meta {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  font-size: 0.75rem;
  color: #9ca3af;
}

.login-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.login-success {
  border-left: 3px solid #10b981;
}

.login-failed {
  border-left: 3px solid #ef4444;
}

.login-icon {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.login-success .login-icon {
  background: #d1fae5;
  color: #065f46;
}

.login-failed .login-icon {
  background: #fee2e2;
  color: #991b1b;
}

.login-content {
  flex: 1;
  min-width: 0;
}

.login-header {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.25rem;
}

.login-user {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.875rem;
}

.login-status {
  background: #f3f4f6;
  color: #374151;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.login-success .login-status {
  background: #d1fae5;
  color: #065f46;
}

.login-failed .login-status {
  background: #fee2e2;
  color: #991b1b;
}

.login-meta {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  font-size: 0.75rem;
  color: #9ca3af;
  flex-wrap: wrap;
}

.login-error {
  color: #dc2626;
  font-weight: 500;
}

.no-activity,
.no-logins {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #6b7280;
}

.no-activity i,
.no-logins i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
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

.btn-primary {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
  border-color: #2563eb;
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
  .realtime-audit-widget {
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
  
  .activity-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .login-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .widget-actions {
    flex-direction: column;
  }
}
</style>

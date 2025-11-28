<template>
  <div class="audit-timeline">
    <div v-if="loading" class="timeline-loading">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
      </div>
      <p>Cargando cronología de auditoría...</p>
    </div>

    <div v-else-if="data.length === 0" class="timeline-empty">
      <div class="empty-icon">
        <i class="fas fa-history"></i>
      </div>
      <h3>No hay actividad</h3>
      <p>No se encontraron registros de auditoría para mostrar.</p>
    </div>

    <div v-else class="timeline-container">
      <div class="timeline-header">
        <h3>Cronología de Auditoría</h3>
        <div class="timeline-stats">
          <span>{{ data.length }} eventos</span>
        </div>
      </div>

      <div class="timeline">
        <div
          v-for="(item, index) in data"
          :key="item.id"
          class="timeline-item"
          :class="{ 'last': index === data.length - 1 }"
        >
          <div class="timeline-marker">
            <div class="marker-icon" :class="getMarkerClass(item)">
              <i :class="getMarkerIcon(item)"></i>
            </div>
          </div>

          <div class="timeline-content">
            <div class="timeline-card">
              <div class="card-header">
                <div class="card-title">
                  <h4>{{ getItemTitle(item) }}</h4>
                  <div class="card-meta">
                    <span class="item-type">{{ getItemType(item) }}</span>
                    <span class="item-status" :class="getStatusClass(item)">
                      {{ getItemStatus(item) }}
                    </span>
                    <span class="item-time">{{ formatDateTime(item.timestamp || item.login_time) }}</span>
                  </div>
                </div>
                <div class="card-actions">
                  <button
                    @click="$emit('view-details', item, auditType)"
                    class="btn btn-sm btn-outline"
                  >
                    <i class="fas fa-eye"></i>
                    Ver Detalles
                  </button>
                </div>
              </div>

              <div class="card-body">
                <div class="item-info">
                  <div class="info-grid">
                    <div class="info-item">
                      <i class="fas fa-user"></i>
                      <span>{{ item.usuario || 'Usuario Anónimo' }}</span>
                    </div>
                    <div class="info-item">
                      <i class="fas fa-globe"></i>
                      <span>{{ item.ip_address || 'N/A' }}</span>
                    </div>
                    <div v-if="auditType === 'activity' || auditType === 'both'" class="info-item">
                      <i class="fas fa-cube"></i>
                      <span>{{ item.modelo }}</span>
                    </div>
                    <div v-if="auditType === 'login' || auditType === 'both'" class="info-item">
                      <i class="fas fa-clock"></i>
                      <span>{{ formatDuration(item.session_duration) }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="auditType === 'activity' || auditType === 'both'" class="item-description">
                  <h5>Descripción</h5>
                  <p>{{ item.descripcion }}</p>
                </div>

                <div v-if="auditType === 'login' || auditType === 'both'" class="session-details">
                  <h5>Detalles de Sesión</h5>
                  <div class="session-info">
                    <div class="session-item">
                      <span class="session-label">Inicio:</span>
                      <span class="session-value">{{ formatDateTime(item.login_time) }}</span>
                    </div>
                    <div v-if="item.logout_time" class="session-item">
                      <span class="session-label">Cierre:</span>
                      <span class="session-value">{{ formatDateTime(item.logout_time) }}</span>
                    </div>
                    <div v-if="item.failure_reason" class="session-item">
                      <span class="session-label">Error:</span>
                      <span class="session-value error">{{ item.failure_reason }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="item.datos_antes || item.datos_despues" class="data-changes">
                  <h5>Cambios de Datos</h5>
                  <div class="changes-grid">
                    <div v-if="item.datos_antes" class="change-item">
                      <span class="change-label">Antes:</span>
                      <pre class="change-data">{{ formatJson(item.datos_antes) }}</pre>
                    </div>
                    <div v-if="item.datos_despues" class="change-item">
                      <span class="change-label">Después:</span>
                      <pre class="change-data">{{ formatJson(item.datos_despues) }}</pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuditTimeline',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    auditType: {
      type: String,
      default: 'activity',
      validator: (value) => ['activity', 'login', 'both'].includes(value)
    }
  },
  emits: ['view-details'],
  methods: {
    getItemTitle(item) {
      if (this.auditType === 'activity' || this.auditType === 'both') {
        return `${item.accion_display || item.accion} - ${item.modelo}`
      } else if (this.auditType === 'login') {
        return `Login ${item.success ? 'Exitoso' : 'Fallido'}`
      }
      return 'Evento de Auditoría'
    },

    getItemType(item) {
      if (this.auditType === 'activity' || this.auditType === 'both') {
        return 'Actividad'
      } else if (this.auditType === 'login') {
        return 'Login'
      }
      return 'Evento'
    },

    getItemStatus(item) {
      if (this.auditType === 'activity' || this.auditType === 'both') {
        return item.accion_display || item.accion
      } else if (this.auditType === 'login') {
        return item.success ? 'Exitoso' : 'Fallido'
      }
      return 'Completado'
    },

    getMarkerClass(item) {
      if (this.auditType === 'activity' || this.auditType === 'both') {
        const actionClasses = {
          'login': 'marker-login',
          'logout': 'marker-logout',
          'create': 'marker-create',
          'update': 'marker-update',
          'delete': 'marker-delete',
          'view': 'marker-view',
          'download': 'marker-download',
          'upload': 'marker-upload',
          'analysis': 'marker-analysis',
          'training': 'marker-training',
          'report': 'marker-report',
          'error': 'marker-error'
        }
        return actionClasses[item.accion] || 'marker-default'
      } else if (this.auditType === 'login') {
        return item.success ? 'marker-success' : 'marker-error'
      }
      return 'marker-default'
    },

    getMarkerIcon(item) {
      if (this.auditType === 'activity' || this.auditType === 'both') {
        const actionIcons = {
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
        return actionIcons[item.accion] || 'fas fa-circle'
      } else if (this.auditType === 'login') {
        return item.success ? 'fas fa-check-circle' : 'fas fa-times-circle'
      }
      return 'fas fa-circle'
    },

    getStatusClass(item) {
      if (this.auditType === 'login' || this.auditType === 'both') {
        return item.success ? 'status-success' : 'status-error'
      }
      return 'status-default'
    },

    formatDateTime(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    formatDuration(durationString) {
      if (!durationString) return 'N/A'
      
      // Parse duration string (e.g., "1:23:45")
      const parts = durationString.split(':')
      if (parts.length === 3) {
        const hours = Number.parseInt(parts[0])
        const minutes = Number.parseInt(parts[1])
        const seconds = Number.parseInt(parts[2])
        
        if (hours > 0) {
          return `${hours}h ${minutes}m`
        } else if (minutes > 0) {
          return `${minutes}m ${seconds}s`
        } else {
          return `${seconds}s`
        }
      }
      
      return durationString
    },

    formatJson(data) {
      try {
        return JSON.stringify(data, null, 2)
      } catch {
        return data
      }
    }
  }
}
</script>

<style scoped>
.audit-timeline {
  width: 100%;
}

.timeline-loading,
.timeline-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.loading-spinner {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #3b82f6;
}

.empty-icon {
  font-size: 3rem;
  color: #d1d5db;
  margin-bottom: 1rem;
}

.empty-icon i {
  opacity: 0.5;
}

.timeline-empty h3 {
  margin: 0 0 0.5rem 0;
  color: #374151;
  font-size: 1.25rem;
  font-weight: 600;
}

.timeline-empty p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.timeline-container {
  width: 100%;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.timeline-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.timeline-stats {
  color: #6b7280;
  font-size: 0.875rem;
}

.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 1rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e5e7eb;
}

.timeline-item {
  position: relative;
  margin-bottom: 2rem;
}

.timeline-item.last {
  margin-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: -2rem;
  top: 0.5rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  z-index: 2;
}

.marker-icon {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
}

.marker-login {
  background: #dbeafe;
  color: #1e40af;
}

.marker-logout {
  background: #fef3c7;
  color: #92400e;
}

.marker-create {
  background: #d1fae5;
  color: #065f46;
}

.marker-update {
  background: #dbeafe;
  color: #1e40af;
}

.marker-delete {
  background: #fee2e2;
  color: #991b1b;
}

.marker-view {
  background: #f3e8ff;
  color: #7c3aed;
}

.marker-download {
  background: #ecfdf5;
  color: #047857;
}

.marker-upload {
  background: #f0f9ff;
  color: #0369a1;
}

.marker-analysis {
  background: #fef3c7;
  color: #92400e;
}

.marker-training {
  background: #f3e8ff;
  color: #7c3aed;
}

.marker-report {
  background: #ecfdf5;
  color: #047857;
}

.marker-error {
  background: #fee2e2;
  color: #991b1b;
}

.marker-success {
  background: #d1fae5;
  color: #065f46;
}

.marker-default {
  background: #f3f4f6;
  color: #374151;
}

.timeline-content {
  margin-left: 1rem;
}

.timeline-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  overflow: hidden;
  transition: all 0.2s;
}

.timeline-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.card-header {
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #f3f4f6;
}

.card-title h4 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
}

.card-meta {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.item-type {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.item-status {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-success {
  background: #d1fae5;
  color: #065f46;
}

.status-error {
  background: #fee2e2;
  color: #991b1b;
}

.status-default {
  background: #f3f4f6;
  color: #374151;
}

.item-time {
  color: #6b7280;
  font-size: 0.75rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
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

.card-body {
  padding: 1rem 1.25rem;
}

.item-info {
  margin-bottom: 1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.info-item i {
  width: 1rem;
  color: #9ca3af;
}

.item-description,
.session-details,
.data-changes {
  margin-bottom: 1rem;
}

.item-description h5,
.session-details h5,
.data-changes h5 {
  margin: 0 0 0.5rem 0;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 600;
}

.item-description p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
}

.session-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-label {
  color: #9ca3af;
  font-size: 0.75rem;
  font-weight: 500;
}

.session-value {
  color: #374151;
  font-size: 0.875rem;
}

.session-value.error {
  color: #dc2626;
}

.changes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.change-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.change-label {
  color: #9ca3af;
  font-size: 0.75rem;
  font-weight: 500;
}

.change-data {
  background: #f8fafc;
  padding: 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  color: #374151;
  margin: 0;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}

/* Responsive */
@media (max-width: 768px) {
  .timeline {
    padding-left: 1.5rem;
  }
  
  .timeline::before {
    left: 0.75rem;
  }
  
  .timeline-marker {
    left: -1.5rem;
    width: 1.5rem;
    height: 1.5rem;
  }
  
  .marker-icon {
    width: 1.25rem;
    height: 1.25rem;
    font-size: 0.625rem;
  }
  
  .timeline-content {
    margin-left: 0.5rem;
  }
  
  .card-header {
    padding: 0.75rem 1rem;
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
  }
  
  .card-body {
    padding: 0.75rem 1rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .changes-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .timeline-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .card-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .card-actions {
    width: 100%;
    justify-content: center;
  }
  
  .btn {
    flex: 1;
    justify-content: center;
  }
}
</style>

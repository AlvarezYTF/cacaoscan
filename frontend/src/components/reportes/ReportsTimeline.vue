<template>
  <div class="reports-timeline">
    <div v-if="loading" class="timeline-loading">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
      </div>
      <p>Cargando reportes...</p>
    </div>

    <div v-else-if="reports.length === 0" class="timeline-empty">
      <div class="empty-icon">
        <i class="fas fa-chart-bar"></i>
      </div>
      <h3>No hay reportes</h3>
      <p>No se encontraron reportes que coincidan con los filtros aplicados.</p>
    </div>

    <div v-else class="timeline-container">
      <div class="timeline-header">
        <h3>Cronología de Reportes</h3>
        <div class="timeline-stats">
          <span>{{ reports.length }} reportes</span>
        </div>
      </div>

      <div class="timeline">
        <div
          v-for="(report, index) in reports"
          :key="report.id"
          class="timeline-item"
          :class="{ 'last': index === reports.length - 1 }"
        >
          <div class="timeline-marker">
            <div class="marker-icon" :class="getStatusClass(report.estado)">
              <i :class="getStatusIcon(report.estado)"></i>
            </div>
          </div>

          <div class="timeline-content">
            <div class="timeline-card">
              <div class="card-header">
                <div class="card-title">
                  <h4>{{ report.titulo }}</h4>
                  <div class="card-meta">
                    <span class="report-type">{{ getReportTypeLabel(report.tipo_reporte) }}</span>
                    <span class="report-format">{{ report.formato.toUpperCase() }}</span>
                    <span class="report-date">{{ formatDate(report.fecha_solicitud) }}</span>
                  </div>
                </div>
                <div class="card-status">
                  <div class="status-indicator" :class="getStatusClass(report.estado)">
                    <i :class="getStatusIcon(report.estado)"></i>
                    <span>{{ getStatusLabel(report.estado) }}</span>
                  </div>
                </div>
              </div>

              <div class="card-body">
                <div v-if="report.descripcion" class="report-description">
                  <p>{{ report.descripcion }}</p>
                </div>

                <div class="report-info">
                  <div class="info-grid">
                    <div class="info-item">
                      <i class="fas fa-user"></i>
                      <span>{{ report.usuario_nombre || 'Usuario' }}</span>
                    </div>
                    <div class="info-item">
                      <i class="fas fa-file"></i>
                      <span>{{ formatFileSize(report.tamaño_archivo) }}</span>
                    </div>
                    <div class="info-item">
                      <i class="fas fa-clock"></i>
                      <span>{{ formatDuration(report.tiempo_generacion) }}</span>
                    </div>
                    <div class="info-item">
                      <i class="fas fa-calendar-alt"></i>
                      <span>{{ formatDateTime(report.fecha_solicitud) }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="report.parametros" class="report-parameters">
                  <h5>Parámetros</h5>
                  <div class="parameters-grid">
                    <div v-if="report.parametros.finca_id" class="param-item">
                      <span class="param-label">Finca:</span>
                      <span class="param-value">{{ report.parametros.finca_nombre || report.parametros.finca_id }}</span>
                    </div>
                    <div v-if="report.parametros.lote_id" class="param-item">
                      <span class="param-label">Lote:</span>
                      <span class="param-value">{{ report.parametros.lote_identificador || report.parametros.lote_id }}</span>
                    </div>
                    <div v-if="report.parametros.custom_type" class="param-item">
                      <span class="param-label">Tipo:</span>
                      <span class="param-value">{{ report.parametros.custom_type }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="card-footer">
                <div class="action-buttons">
                  <button
                    @click="$emit('view', report)"
                    class="btn btn-outline"
                    :disabled="report.estado !== 'completado'"
                  >
                    <i class="fas fa-eye"></i>
                    Ver
                  </button>
                  <button
                    @click="$emit('download', report)"
                    class="btn btn-primary"
                    :disabled="report.estado !== 'completado'"
                  >
                    <i class="fas fa-download"></i>
                    Descargar
                  </button>
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
  name: 'ReportsTimeline',
  props: {
    reports: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['view', 'download'],
  methods: {
    getReportTypeLabel(type) {
      const labels = {
        'calidad': 'Calidad',
        'finca': 'Finca',
        'lote': 'Lote',
        'usuario': 'Usuario',
        'auditoria': 'Auditoría',
        'personalizado': 'Personalizado',
        'metricas': 'Métricas',
        'entrenamiento': 'Entrenamiento'
      }
      return labels[type] || type
    },

    getStatusLabel(status) {
      const labels = {
        'pendiente': 'Pendiente',
        'procesando': 'Procesando',
        'completado': 'Completado',
        'error': 'Error'
      }
      return labels[status] || status
    },

    getStatusClass(status) {
      const classes = {
        'pendiente': 'status-pending',
        'procesando': 'status-processing',
        'completado': 'status-completed',
        'error': 'status-error'
      }
      return classes[status] || 'status-pending'
    },

    getStatusIcon(status) {
      const icons = {
        'pendiente': 'fas fa-clock',
        'procesando': 'fas fa-spinner fa-spin',
        'completado': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle'
      }
      return icons[status] || 'fas fa-clock'
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
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

    formatFileSize(bytes) {
      if (!bytes) return 'N/A'
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    },

    formatDuration(seconds) {
      if (!seconds) return 'N/A'
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}m ${remainingSeconds}s`
    }
  }
}
</script>

<style scoped>
.reports-timeline {
  width: 100%;
}

.timeline-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #6b7280;
}

.loading-spinner {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #3b82f6;
}

.timeline-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
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

.marker-icon.status-pending {
  background: #fde68a;
  color: #7c2d12;
}

.marker-icon.status-processing {
  background: #dbeafe;
  color: #1e40af;
}

.marker-icon.status-completed {
  background: #d1fae5;
  color: #047857;
}

.marker-icon.status-error {
  background: #fecdd3;
  color: #991b1b;
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

.report-type {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.report-format {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.report-date {
  color: #6b7280;
  font-size: 0.75rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-pending {
  color: #7c2d12;
}

.status-processing {
  color: #3b82f6;
}

.status-completed {
  color: #10b981;
}

.status-error {
  color: #991b1b;
}

.card-body {
  padding: 1rem 1.25rem;
}

.report-description {
  margin-bottom: 1rem;
}

.report-description p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
}

.report-info {
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

.report-parameters {
  background: #f8fafc;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.report-parameters h5 {
  margin: 0 0 0.5rem 0;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 600;
}

.parameters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.param-label {
  color: #9ca3af;
  font-size: 0.75rem;
  font-weight: 500;
}

.param-value {
  color: #374151;
  font-size: 0.75rem;
  font-weight: 600;
}

.card-footer {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid #f3f4f6;
  background: #f8fafc;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  background-color: #1f4e79;
  color: #ffffff;
  border-color: #1f4e79;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1a3d5b;
  border-color: #1a3d5b;
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
  
  .card-footer {
    padding: 0.5rem 1rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .parameters-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    justify-content: center;
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
  
  .action-buttons {
    flex-direction: column;
  }
  
  .btn {
    justify-content: center;
  }
}
</style>

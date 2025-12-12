<template>
  <div class="report-card" :class="{ 'selected': selected }">
    <div class="card-header">
      <div class="card-title">
        <h4>{{ report.titulo }}</h4>
        <div class="card-meta">
          <span class="report-type">{{ getReportTypeLabel(report.tipo_reporte) }}</span>
          <span class="report-format">{{ report.formato.toUpperCase() }}</span>
        </div>
      </div>
      <div class="card-actions">
        <button
          @click="$emit('select', report.id)"
          class="select-btn"
          :class="{ 'selected': selected }"
        >
          <i class="fas fa-check"></i>
        </button>
      </div>
    </div>

    <div class="card-body">
      <div class="report-info">
        <div class="info-item">
          <i class="fas fa-calendar"></i>
          <span>{{ formatReportDate(report.fecha_solicitud) }}</span>
        </div>
        <div class="info-item">
          <i class="fas fa-user"></i>
          <span>{{ report.usuario_nombre || 'Usuario' }}</span>
        </div>
        <div class="info-item">
          <i class="fas fa-clock"></i>
          <span>{{ getStatusLabel(report.estado) }}</span>
        </div>
      </div>

      <div v-if="report.descripcion" class="report-description">
        <p>{{ report.descripcion }}</p>
      </div>

      <div class="report-stats">
        <div class="stat-item">
          <span class="stat-label">Tamaño</span>
          <span class="stat-value">{{ formatReportFileSize(report.tamaño_archivo || report.tamano_archivo_mb * 1024 * 1024) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Duración</span>
          <span class="stat-value">{{ formatReportDuration(report.tiempo_generacion_segundos || report.tiempo_generacion) }}</span>
        </div>
      </div>
    </div>

    <div class="card-footer">
      <div class="status-indicator" :class="getStatusClass(report.estado)">
        <i :class="getStatusIcon(report.estado)"></i>
        <span>{{ getStatusLabel(report.estado) }}</span>
      </div>

      <div class="action-buttons">
        <button
          @click="$emit('view', report)"
          class="btn btn-sm btn-outline"
          :disabled="report.estado !== 'completado'"
        >
          <i class="fas fa-eye"></i>
          Ver
        </button>
        <button
          @click="$emit('download', report)"
          class="btn btn-sm btn-primary"
          :disabled="report.estado !== 'completado'"
        >
          <i class="fas fa-download"></i>
          Descargar
        </button>
        <button
          @click="$emit('delete', report)"
          class="btn btn-sm btn-danger"
        >
          <i class="fas fa-trash"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  formatReportType,
  formatReportStatus,
  getReportStatusClass,
  getReportStatusIcon,
  formatFileSize,
  formatDuration
} from '@/composables/useReports'
import { useDateFormatting } from '@/composables/useDateFormatting'

const props = defineProps({
  report: {
    type: Object,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  }
})

defineEmits(['view', 'download', 'delete', 'select'])

const { formatDate } = useDateFormatting()

const getReportTypeLabel = (type) => formatReportType(type)
const getStatusLabel = (status) => formatReportStatus(status)
const getStatusClass = (status) => getReportStatusClass(status)
const getStatusIcon = (status) => getReportStatusIcon(status)

const formatReportDate = (dateString) => formatDate(dateString)
const formatReportFileSize = (bytes) => {
  if (!bytes) return 'N/A'
  return formatFileSize(bytes)
}
const formatReportDuration = (seconds) => {
  if (!seconds && seconds !== 0) return 'N/A'
  return formatDuration(seconds)
}
</script>

<style scoped>
.report-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  overflow: hidden;
  transition: all 0.2s;
  cursor: pointer;
}

.report-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.report-card.selected {
  border-color: #3b82f6;
  background: #eff6ff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.card-header {
  padding: 1rem 1.25rem 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.select-btn {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid #d1d5db;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.select-btn:hover {
  border-color: #3b82f6;
}

.select-btn.selected {
  background: #1e40af;
  border-color: #1e40af;
  color: #ffffff;
}

.card-body {
  padding: 0 1.25rem;
}

.report-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
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

.report-description {
  margin-bottom: 1rem;
}

.report-description p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.report-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  color: #9ca3af;
  font-size: 0.75rem;
  font-weight: 500;
}

.stat-value {
  color: #374151;
  font-size: 0.875rem;
  font-weight: 600;
}

.card-footer {
  padding: 0.75rem 1.25rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f3f4f6;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-pending {
  color: #f59e0b;
}

.status-processing {
  color: #3b82f6;
}

.status-completed {
  color: #10b981;
}

.status-error {
  color: #ef4444;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  background-color: #1e40af;
  color: #ffffff;
  border-color: #1e40af;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1e3a8a;
  border-color: #1e3a8a;
}

.btn-danger {
  background-color: #b91c1c;
  color: #ffffff;
  border-color: #b91c1c;
}

.btn-danger:hover:not(:disabled) {
  background-color: #991b1b;
  border-color: #991b1b;
}

/* Responsive */
@media (max-width: 640px) {
  .card-header {
    padding: 0.75rem 1rem 0.5rem;
  }
  
  .card-body {
    padding: 0 1rem;
  }
  
  .card-footer {
    padding: 0.5rem 1rem 0.75rem;
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .report-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>

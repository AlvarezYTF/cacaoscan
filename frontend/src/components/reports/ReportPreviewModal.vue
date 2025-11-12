<template>
  <div class="report-preview-modal" @click="closeModal">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <div class="header-content">
          <div class="header-icon">
            <i class="fas fa-file-alt"></i>
          </div>
          <div class="header-text">
            <h3>{{ report.titulo }}</h3>
            <p>Vista previa del reporte</p>
          </div>
        </div>
        <button class="close-btn" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
          </div>
          <p>Cargando vista previa...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <div class="error-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <h4>Error al cargar la vista previa</h4>
          <p>{{ error }}</p>
          <button @click="loadPreview" class="btn btn-primary">
            <i class="fas fa-retry"></i>
            Reintentar
          </button>
        </div>

        <div v-else-if="previewData" class="preview-content">
          <!-- Información del reporte -->
          <div class="report-info">
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Tipo:</span>
                <span class="info-value">{{ getReportTypeLabel(report.tipo_reporte) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Formato:</span>
                <span class="info-value">{{ report.formato.toUpperCase() }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Estado:</span>
                <span class="info-value" :class="getStatusClass(report.estado)">
                  {{ getStatusLabel(report.estado) }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">Creado:</span>
                <span class="info-value">{{ formatDateTime(report.fecha_solicitud) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Tamaño:</span>
                <span class="info-value">{{ formatFileSize(report.tamaño_archivo) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Duración:</span>
                <span class="info-value">{{ formatDuration(report.tiempo_generacion) }}</span>
              </div>
            </div>
          </div>

          <!-- Descripción -->
          <div v-if="report.descripcion" class="report-description">
            <h4>Descripción</h4>
            <p>{{ report.descripcion }}</p>
          </div>

          <!-- Parámetros -->
          <div v-if="report.parametros" class="report-parameters">
            <h4>Parámetros</h4>
            <div class="parameters-grid">
              <div v-for="(value, key) in report.parametros" :key="key" class="param-item">
                <span class="param-label">{{ formatParameterLabel(key) }}:</span>
                <span class="param-value">{{ formatParameterValue(value) }}</span>
              </div>
            </div>
          </div>

          <!-- Filtros -->
          <div v-if="report.filtros" class="report-filters">
            <h4>Filtros Aplicados</h4>
            <div class="filters-grid">
              <div v-for="(value, key) in report.filtros" :key="key" class="filter-item">
                <span class="filter-label">{{ formatFilterLabel(key) }}:</span>
                <span class="filter-value">{{ formatFilterValue(value) }}</span>
              </div>
            </div>
          </div>

          <!-- Vista previa del contenido -->
          <div v-if="previewData.content" class="preview-data">
            <h4>Vista Previa del Contenido</h4>
            <div class="content-preview">
              <!-- PDF Preview -->
              <div v-if="report.formato === 'pdf'" class="pdf-preview">
                <iframe
                  :src="previewData.content"
                  width="100%"
                  height="600px"
                  style="border: none;"
                  :title="`Vista previa del reporte ${report.nombre || 'PDF'}`"
                ></iframe>
              </div>

              <!-- Excel Preview -->
              <div v-else-if="report.formato === 'excel'" class="excel-preview">
                <div class="table-container">
                  <table class="data-table" aria-label="Vista previa de datos del reporte Excel">
                    <caption class="sr-only">Tabla mostrando los datos del reporte en formato Excel con columnas y filas</caption>
                    <thead>
                      <tr>
                        <th v-for="header in previewData.headers" :key="header">
                          {{ header }}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, index) in previewData.rows" :key="index">
                        <td v-for="cell in row" :key="cell">
                          {{ cell }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="preview-note">
                  <i class="fas fa-info-circle"></i>
                  <span>Mostrando las primeras {{ previewData.rows.length }} filas</span>
                </div>
              </div>

              <!-- CSV Preview -->
              <div v-else-if="report.formato === 'csv'" class="csv-preview">
                <div class="table-container">
                  <table class="data-table" aria-label="Vista previa de datos del reporte CSV">
                    <caption class="sr-only">Tabla mostrando los datos del reporte en formato CSV con columnas y filas</caption>
                    <thead>
                      <tr>
                        <th v-for="header in previewData.headers" :key="header">
                          {{ header }}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, index) in previewData.rows" :key="index">
                        <td v-for="cell in row" :key="cell">
                          {{ cell }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="preview-note">
                  <i class="fas fa-info-circle"></i>
                  <span>Mostrando las primeras {{ previewData.rows.length }} filas</span>
                </div>
              </div>

              <!-- JSON Preview -->
              <div v-else-if="report.formato === 'json'" class="json-preview">
                <pre class="json-content">{{ formatJson(previewData.content) }}</pre>
              </div>

              <!-- Default Preview -->
              <div v-else class="default-preview">
                <div class="preview-placeholder">
                  <i class="fas fa-file-alt"></i>
                  <p>Vista previa no disponible para este formato</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Estadísticas del reporte -->
          <div v-if="previewData.statistics" class="report-statistics">
            <h4>Estadísticas</h4>
            <div class="stats-grid">
              <div v-for="(value, key) in previewData.statistics" :key="key" class="stat-item">
                <span class="stat-label">{{ formatStatLabel(key) }}:</span>
                <span class="stat-value">{{ formatStatValue(value) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <div class="footer-left">
          <button
            @click="$emit('download', report)"
            class="btn btn-primary"
            :disabled="report.estado !== 'completado'"
          >
            <i class="fas fa-download"></i>
            Descargar Reporte
          </button>
        </div>

        <div class="footer-right">
          <button @click="closeModal" class="btn btn-outline">
            Cerrar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useReportsStore } from '@/stores/reports'

export default {
  name: 'ReportPreviewModal',
  props: {
    report: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'download'],
  setup(props, { emit }) {
    const reportsStore = useReportsStore()
    const loading = ref(false)
    const error = ref(null)
    const previewData = ref(null)

    const loadPreview = async () => {
      if (props.report.estado !== 'completado') {
        return
      }

      try {
        loading.value = true
        error.value = null
        
        const response = await reportsStore.getReportPreview(props.report.id)
        previewData.value = response.data
      } catch (err) {
        console.error('Error loading preview:', err)
        error.value = err.response?.data?.detail || 'Error al cargar la vista previa'
      } finally {
        loading.value = false
      }
    }

    const closeModal = () => {
      emit('close')
    }

    const getReportTypeLabel = (type) => {
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
    }

    const getStatusLabel = (status) => {
      const labels = {
        'pendiente': 'Pendiente',
        'procesando': 'Procesando',
        'completado': 'Completado',
        'error': 'Error'
      }
      return labels[status] || status
    }

    const getStatusClass = (status) => {
      const classes = {
        'pendiente': 'status-pending',
        'procesando': 'status-processing',
        'completado': 'status-completed',
        'error': 'status-error'
      }
      return classes[status] || 'status-pending'
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return 'N/A'
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }

    const formatDuration = (seconds) => {
      if (!seconds) return 'N/A'
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}m ${remainingSeconds}s`
    }

    // Función auxiliar para capitalizar palabras sin usar replace() con regex
    const capitalizeWords = (str) => {
      return str.split(' ').map(word => {
        if (word.length === 0) return word
        return word[0].toUpperCase() + word.slice(1).toLowerCase()
      }).join(' ')
    }

    const formatParameterLabel = (key) => {
      const labels = {
        'finca_id': 'Finca',
        'lote_id': 'Lote',
        'custom_type': 'Tipo Personalizado',
        'analysis_depth': 'Profundidad',
        'model_type': 'Tipo de Modelo',
        'target_metric': 'Variable Objetivo',
        'include_charts': 'Incluir Gráficos',
        'include_recommendations': 'Incluir Recomendaciones',
        'include_raw_data': 'Incluir Datos Crudos',
        'include_summary': 'Incluir Resumen',
        'include_lotes': 'Incluir Lotes',
        'scheduled': 'Programado',
        'schedule_frequency': 'Frecuencia',
        'schedule_time': 'Hora',
        'schedule_email': 'Email',
        'schedule_retention': 'Retención'
      }
      return labels[key] || capitalizeWords(key.replaceAll('_', ' '))
    }

    const formatParameterValue = (value) => {
      if (typeof value === 'boolean') {
        return value ? 'Sí' : 'No'
      }
      if (typeof value === 'object') {
        return JSON.stringify(value)
      }
      return value
    }

    const formatFilterLabel = (key) => {
      const labels = {
        'fecha_desde': 'Fecha Desde',
        'fecha_hasta': 'Fecha Hasta',
        'usuario_id': 'Usuario',
        'calidad_minima': 'Calidad Mínima',
        'confianza_minima': 'Confianza Mínima',
        'variedad': 'Variedad',
        'region': 'Región',
        'municipio': 'Municipio',
        'altitud_minima': 'Altitud Mínima',
        'altitud_maxima': 'Altitud Máxima'
      }
      return labels[key] || capitalizeWords(key.replaceAll('_', ' '))
    }

    const formatFilterValue = (value) => {
      if (typeof value === 'number') {
        return value.toLocaleString()
      }
      return value
    }

    const formatStatLabel = (key) => {
      const labels = {
        'total_records': 'Total de Registros',
        'total_pages': 'Total de Páginas',
        'generation_time': 'Tiempo de Generación',
        'file_size': 'Tamaño del Archivo',
        'data_points': 'Puntos de Datos',
        'charts_count': 'Número de Gráficos',
        'tables_count': 'Número de Tablas'
      }
      return labels[key] || capitalizeWords(key.replaceAll('_', ' '))
    }

    // Reutilizar formatFilterValue en lugar de duplicar código
    const formatStatValue = formatFilterValue

    const formatJson = (data) => {
      try {
        return JSON.stringify(data, null, 2)
      } catch {
        return data
      }
    }

    onMounted(() => {
      loadPreview()
    })

    return {
      loading,
      error,
      previewData,
      loadPreview,
      closeModal,
      getReportTypeLabel,
      getStatusLabel,
      getStatusClass,
      formatDateTime,
      formatFileSize,
      formatDuration,
      formatParameterLabel,
      formatParameterValue,
      formatFilterLabel,
      formatFilterValue,
      formatStatLabel,
      formatStatValue,
      formatJson
    }
  }
}
</script>

<style scoped>
.report-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 1000px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: linear-gradient(135deg, #4c51bf 0%, #553c9a 100%);
  color: #ffffff;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  width: 3rem;
  height: 3rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.header-text h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-text p {
  margin: 0.25rem 0 0 0;
  color: rgba(255, 255, 255, 0.95);
  font-size: 0.875rem;
}

.close-btn {
  background: rgba(0, 0, 0, 0.2);
  border: none;
  color: #ffffff;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.3);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.loading-state,
.error-state {
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

.error-icon {
  font-size: 3rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.error-state h4 {
  margin: 0 0 0.5rem 0;
  color: #374151;
  font-size: 1.25rem;
  font-weight: 600;
}

.error-state p {
  margin: 0 0 1.5rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.report-info {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  color: #9ca3af;
  font-size: 0.75rem;
  font-weight: 500;
}

.info-value {
  color: #374151;
  font-size: 0.875rem;
  font-weight: 600;
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

.report-description,
.report-parameters,
.report-filters,
.preview-data,
.report-statistics {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.report-description h4,
.report-parameters h4,
.report-filters h4,
.preview-data h4,
.report-statistics h4 {
  margin: 0 0 1rem 0;
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
}

.report-description p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
}

.parameters-grid,
.filters-grid,
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.param-item,
.filter-item,
.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.param-label,
.filter-label,
.stat-label {
  color: #9ca3af;
  font-size: 0.75rem;
  font-weight: 500;
}

.param-value,
.filter-value,
.stat-value {
  color: #374151;
  font-size: 0.875rem;
  font-weight: 600;
}

.content-preview {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.pdf-preview iframe {
  border: none;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.data-table td {
  color: #6b7280;
  font-size: 0.875rem;
}

.preview-note {
  padding: 0.75rem;
  background: #f0f9ff;
  color: #0369a1;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.json-preview {
  background: #1f2937;
  color: #f9fafb;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
}

.json-content {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.5;
}

.default-preview {
  padding: 3rem;
  text-align: center;
}

.preview-placeholder {
  color: #9ca3af;
}

.preview-placeholder i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.preview-placeholder p {
  margin: 0;
  font-size: 0.875rem;
}

.modal-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
}

.footer-left,
.footer-right {
  display: flex;
  gap: 0.75rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
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
  background-color: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
  border-color: #2563eb;
}

/* Responsive */
@media (max-width: 768px) {
  .modal-container {
    margin: 0.5rem;
    max-height: 95vh;
  }
  
  .modal-header {
    padding: 1rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
  
  .modal-footer {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }
  
  .footer-left,
  .footer-right {
    width: 100%;
    justify-content: center;
  }
  
  .info-grid,
  .parameters-grid,
  .filters-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .pdf-preview iframe {
    height: 400px;
  }
}

@media (max-width: 480px) {
  .report-preview-modal {
    padding: 0.25rem;
  }
  
  .modal-container {
    margin: 0;
    border-radius: 0;
    max-height: 100vh;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .header-icon {
    width: 2.5rem;
    height: 2.5rem;
    font-size: 1rem;
  }
  
  .header-text h3 {
    font-size: 1.25rem;
  }
  
  .btn {
    padding: 0.625rem 1rem;
    font-size: 0.8125rem;
  }
}
</style>

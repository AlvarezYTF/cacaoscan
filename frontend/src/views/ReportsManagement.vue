<template>
  <div class="reports-management">
    <div class="container-fluid">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h2 class="mb-1">
                <i class="fas fa-file-alt text-primary"></i>
                Gestión de Reportes
              </h2>
              <p class="text-muted mb-0">Genera y descarga reportes de análisis de cacao</p>
            </div>
            <button
              @click="mostrarGenerador = !mostrarGenerador"
              class="btn btn-primary"
            >
              <i class="fas fa-plus"></i>
              {{ mostrarGenerador ? 'Ocultar Generador' : 'Nuevo Reporte' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Generador de Reportes -->
      <div v-if="mostrarGenerador" class="row mb-4">
        <div class="col-12">
          <ReportGenerator
            @reporte-generado="onReporteGenerado"
            @ver-detalles="verDetallesReporte"
          />
        </div>
      </div>

      <!-- Estadísticas -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card stats-card">
            <div class="card-body text-center">
              <i class="fas fa-file-alt fa-2x text-primary mb-2"></i>
              <h4 class="mb-1">{{ estadisticas.total_reportes }}</h4>
              <p class="text-muted mb-0">Total Reportes</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card stats-card">
            <div class="card-body text-center">
              <i class="fas fa-check-circle fa-2x text-success mb-2"></i>
              <h4 class="mb-1">{{ estadisticas.reportes_completados }}</h4>
              <p class="text-muted mb-0">Completados</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card stats-card">
            <div class="card-body text-center">
              <i class="fas fa-spinner fa-2x text-warning mb-2"></i>
              <h4 class="mb-1">{{ estadisticas.reportes_generando }}</h4>
              <p class="text-muted mb-0">Generando</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card stats-card">
            <div class="card-body text-center">
              <i class="fas fa-exclamation-triangle fa-2x text-danger mb-2"></i>
              <h4 class="mb-1">{{ estadisticas.reportes_fallidos }}</h4>
              <p class="text-muted mb-0">Fallidos</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Filtros -->
      <div class="row mb-3">
        <div class="col-12">
          <div class="card">
            <div class="card-body">
              <div class="row align-items-center">
                <div class="col-md-3">
                  <label for="tipo-reporte" class="form-label">Tipo de Reporte</label>
                  <select id="tipo-reporte" v-model="filtros.tipo_reporte" class="form-select">
                    <option value="">Todos los tipos</option>
                    <option value="calidad">Calidad</option>
                    <option value="finca">Finca</option>
                    <option value="auditoria">Auditoría</option>
                    <option value="personalizado">Personalizado</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label for="formato-reporte" class="form-label">Formato</label>
                  <select id="formato-reporte" v-model="filtros.formato" class="form-select">
                    <option value="">Todos los formatos</option>
                    <option value="pdf">PDF</option>
                    <option value="excel">Excel</option>
                    <option value="csv">CSV</option>
                    <option value="json">JSON</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label for="estado-reporte" class="form-label">Estado</label>
                  <select id="estado-reporte" v-model="filtros.estado" class="form-select">
                    <option value="">Todos los estados</option>
                    <option value="completado">Completado</option>
                    <option value="generando">Generando</option>
                    <option value="fallido">Fallido</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <div class="d-flex gap-2">
                    <button @click="aplicarFiltros" class="btn btn-primary">
                      <i class="fas fa-filter"></i>
                      Filtrar
                    </button>
                    <button @click="limpiarFiltros" class="btn btn-secondary">
                      <i class="fas fa-eraser"></i>
                      Limpiar
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabla de Reportes -->
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">
                <i class="fas fa-list"></i>
                Lista de Reportes
              </h5>
            </div>
            <div class="card-body">
              <div v-if="cargando" class="text-center py-4">
                <div class="spinner-border text-primary" aria-label="Cargando reportes">
                  <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2 text-muted">Cargando reportes...</p>
              </div>

              <div v-else-if="reportes.length === 0" class="text-center py-4">
                <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No hay reportes disponibles</h5>
                <p class="text-muted">Genera tu primer reporte usando el botón "Nuevo Reporte"</p>
              </div>

              <div v-else class="table-responsive">
                <table class="table table-hover" aria-label="Tabla de reportes generados">
                  <caption class="sr-only">Tabla de reportes mostrando título, tipo, formato, estado, fecha de solicitud, tamaño y acciones disponibles</caption>
                  <thead>
                    <tr>
                      <th>Título</th>
                      <th>Tipo</th>
                      <th>Formato</th>
                      <th>Estado</th>
                      <th>Fecha Solicitud</th>
                      <th>Tamaño</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="reporte in reportes" :key="reporte.id">
                      <td>
                        <div>
                          <strong>{{ reporte.titulo }}</strong>
                          <br>
                          <small class="text-muted">{{ reporte.descripcion || 'Sin descripción' }}</small>
                        </div>
                      </td>
                      <td>
                        <span class="badge bg-info">
                          {{ reporte.tipo_reporte_display }}
                        </span>
                      </td>
                      <td>
                        <span class="badge bg-secondary">
                          {{ reporte.formato_display }}
                        </span>
                      </td>
                      <td>
                        <span
                          class="badge"
                          :class="{
                            'bg-success': reporte.estado === 'completado',
                            'bg-warning': reporte.estado === 'generando',
                            'bg-danger': reporte.estado === 'fallido'
                          }"
                        >
                          {{ reporte.estado_display }}
                        </span>
                      </td>
                      <td>
                        <small>{{ formatearFecha(reporte.fecha_solicitud) }}</small>
                      </td>
                      <td>
                        <small v-if="reporte.tamaño_archivo_mb">
                          {{ reporte.tamaño_archivo_mb }} MB
                        </small>
                        <small v-else class="text-muted">-</small>
                      </td>
                      <td>
                        <div class="btn-group" aria-label="Acciones del reporte">
                          <ReportDownloadButton :reporte="reporte" />
                          <button
                            @click="verDetallesReporte(reporte.id)"
                            class="btn btn-outline-info btn-sm"
                            title="Ver detalles"
                          >
                            <i class="fas fa-eye"></i>
                          </button>
                          <button
                            @click="eliminarReporte(reporte.id)"
                            class="btn btn-outline-danger btn-sm"
                            title="Eliminar"
                          >
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Paginación -->
              <div v-if="totalPages > 1" class="d-flex justify-content-between align-items-center mt-3">
                <small class="text-muted">
                  Mostrando {{ reportes.length }} de {{ totalCount }} reportes
                </small>
                <nav>
                  <ul class="pagination pagination-sm mb-0">
                    <li class="page-item" :class="{ disabled: currentPage === 1 }">
                      <button
                        @click="cambiarPagina(currentPage - 1)"
                        class="page-link"
                        :disabled="currentPage === 1"
                      >
                        Anterior
                      </button>
                    </li>
                    <li
                      v-for="page in paginasVisibles"
                      :key="page"
                      class="page-item"
                      :class="{ active: page === currentPage }"
                    >
                      <button @click="cambiarPagina(page)" class="page-link">
                        {{ page }}
                      </button>
                    </li>
                    <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                      <button
                        @click="cambiarPagina(currentPage + 1)"
                        class="page-link"
                        :disabled="currentPage === totalPages"
                      >
                        Siguiente
                      </button>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Detalles -->
    <div
      v-if="mostrarDetalles"
      class="modal fade show"
      style="display: block;"
      tabindex="-1"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-info-circle"></i>
              Detalles del Reporte
            </h5>
            <button
              @click="mostrarDetalles = false"
              type="button"
              class="btn-close"
            ></button>
          </div>
          <div class="modal-body">
            <div v-if="detallesReporte">
              <div class="row">
                <div class="col-md-6">
                  <h6>Información General</h6>
                  <table class="table table-sm" aria-label="Información general del reporte">
                    <caption class="sr-only">Tabla con información general del reporte mostrando título, tipo y formato</caption>
                    <thead>
                      <tr>
                        <th scope="col">Campo</th>
                        <th scope="col">Valor</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th scope="row">Título:</th>
                        <td>{{ detallesReporte.titulo }}</td>
                      </tr>
                      <tr>
                        <th scope="row">Tipo:</th>
                        <td>{{ detallesReporte.tipo_reporte_display }}</td>
                      </tr>
                      <tr>
                        <th scope="row">Formato:</th>
                        <td>{{ detallesReporte.formato_display }}</td>
                      </tr>
                      <tr>
                        <th scope="row">Estado:</th>
                        <td>
                          <span
                            class="badge"
                            :class="{
                              'bg-success': detallesReporte.estado === 'completado',
                              'bg-warning': detallesReporte.estado === 'generando',
                              'bg-danger': detallesReporte.estado === 'fallido'
                            }"
                          >
                            {{ detallesReporte.estado_display }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="col-md-6">
                  <h6>Información Técnica</h6>
                  <table class="table table-sm" aria-label="Información técnica del reporte">
                    <caption class="sr-only">Tabla con información técnica del reporte mostrando fechas, tiempo de generación y tamaño</caption>
                    <thead>
                      <tr>
                        <th scope="col">Campo</th>
                        <th scope="col">Valor</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th scope="row">Fecha Solicitud:</th>
                        <td>{{ formatearFecha(detallesReporte.fecha_solicitud) }}</td>
                      </tr>
                      <tr>
                        <th scope="row">Fecha Generación:</th>
                        <td>{{ detallesReporte.fecha_generacion ? formatearFecha(detallesReporte.fecha_generacion) : 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th scope="row">Tiempo Generación:</th>
                        <td>{{ detallesReporte.tiempo_generacion_segundos ? `${detallesReporte.tiempo_generacion_segundos}s` : 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th scope="row">Tamaño:</th>
                        <td>{{ detallesReporte.tamaño_archivo_mb ? `${detallesReporte.tamaño_archivo_mb} MB` : 'N/A' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              
              <div v-if="detallesReporte.descripcion" class="mt-3">
                <h6>Descripción</h6>
                <p class="text-muted">{{ detallesReporte.descripcion }}</p>
              </div>

              <div v-if="detallesReporte.mensaje_error" class="mt-3">
                <h6>Error</h6>
                <div class="alert alert-danger">
                  <i class="fas fa-exclamation-triangle"></i>
                  {{ detallesReporte.mensaje_error }}
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button
              @click="mostrarDetalles = false"
              type="button"
              class="btn btn-secondary"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Overlay del Modal -->
    <div
      v-if="mostrarDetalles"
      class="modal-backdrop fade show"
    ></div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import ReportGenerator from '@/components/reportes/ReportGenerator.vue'
import ReportDownloadButton from '@/components/reportes/ReportDownloadButton.vue'

export default {
  name: 'ReportsManagement',
  components: {
    ReportGenerator,
    ReportDownloadButton
  },
  setup() {
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()
    
    const cargando = ref(false)
    const reportes = ref([])
    const estadisticas = ref({
      total_reportes: 0,
      reportes_completados: 0,
      reportes_generando: 0,
      reportes_fallidos: 0
    })
    const mostrarGenerador = ref(false)
    const mostrarDetalles = ref(false)
    const detallesReporte = ref(null)
    
    const filtros = reactive({
      tipo_reporte: '',
      formato: '',
      estado: ''
    })
    
    const paginacion = reactive({
      currentPage: 1,
      pageSize: 20,
      totalCount: 0,
      totalPages: 0
    })
    
    const paginasVisibles = computed(() => {
      const pages = []
      const start = Math.max(1, paginacion.currentPage - 2)
      const end = Math.min(paginacion.totalPages, paginacion.currentPage + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })
    
    const cargarReportes = async () => {
      try {
        cargando.value = true
        
        const params = new URLSearchParams({
          page: paginacion.currentPage.toString(),
          page_size: paginacion.pageSize.toString()
        })
        
        // Agregar filtros
        if (filtros.tipo_reporte) params.append('tipo_reporte', filtros.tipo_reporte)
        if (filtros.formato) params.append('formato', filtros.formato)
        if (filtros.estado) params.append('estado', filtros.estado)
        
        const response = await fetch(`/api/reportes/?${params}`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          reportes.value = data.results
          paginacion.totalCount = data.count
          paginacion.totalPages = data.total_pages
        } else {
          throw new Error('Error al cargar reportes')
        }
        
      } catch (err) {
        notificationStore.addNotification({
          type: 'error',
          title: 'Error',
          message: 'No se pudieron cargar los reportes'
        })
      } finally {
        cargando.value = false
      }
    }
    
    const cargarEstadisticas = async () => {
      try {
        const response = await fetch('/api/reportes/stats/', {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          estadisticas.value = data
        }
      } catch (err) {
        }
    }
    
    const aplicarFiltros = () => {
      paginacion.currentPage = 1
      cargarReportes()
    }
    
    const limpiarFiltros = () => {
      Object.assign(filtros, {
        tipo_reporte: '',
        formato: '',
        estado: ''
      })
      paginacion.currentPage = 1
      cargarReportes()
    }
    
    const cambiarPagina = (page) => {
      if (page >= 1 && page <= paginacion.totalPages) {
        paginacion.currentPage = page
        cargarReportes()
      }
    }
    
    const verDetallesReporte = async (reporteId) => {
      try {
        const response = await fetch(`/api/reportes/${reporteId}/`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          detallesReporte.value = await response.json()
          mostrarDetalles.value = true
        } else {
          throw new Error('Error al cargar detalles del reporte')
        }
      } catch (err) {
        notificationStore.addNotification({
          type: 'error',
          title: 'Error',
          message: 'No se pudieron cargar los detalles del reporte'
        })
      }
    }
    
    const eliminarReporte = async (reporteId) => {
      if (!confirm('¿Estás seguro de que quieres eliminar este reporte?')) {
        return
      }
      
      try {
        const response = await fetch(`/api/reportes/${reporteId}/delete/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          notificationStore.addNotification({
            type: 'success',
            title: 'Reporte eliminado',
            message: 'El reporte se ha eliminado correctamente'
          })
          cargarReportes()
          cargarEstadisticas()
        } else {
          throw new Error('Error al eliminar el reporte')
        }
      } catch (err) {
        notificationStore.addNotification({
          type: 'error',
          title: 'Error',
          message: 'No se pudo eliminar el reporte'
        })
      }
    }
    
    const onReporteGenerado = (reporte) => {
      mostrarGenerador.value = false
      cargarReportes()
      cargarEstadisticas()
    }
    
    const formatearFecha = (fecha) => {
      if (!fecha) return 'N/A'
      return new Date(fecha).toLocaleString('es-ES')
    }
    
    // Auto-refresh cada 30 segundos para reportes en generación
    let refreshInterval = null
    
    const iniciarAutoRefresh = () => {
      refreshInterval = setInterval(() => {
        const tieneGenerando = reportes.value.some(r => r.estado === 'generando')
        if (tieneGenerando) {
          cargarReportes()
          cargarEstadisticas()
        }
      }, 30000)
    }
    
    const detenerAutoRefresh = () => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
        refreshInterval = null
      }
    }
    
    onMounted(() => {
      cargarReportes()
      cargarEstadisticas()
      iniciarAutoRefresh()
    })
    
    // Limpiar interval al desmontar
    const cleanup = () => {
      detenerAutoRefresh()
    }
    
    return {
      cargando,
      reportes,
      estadisticas,
      mostrarGenerador,
      mostrarDetalles,
      detallesReporte,
      filtros,
      paginacion,
      paginasVisibles,
      cargarReportes,
      cargarEstadisticas,
      aplicarFiltros,
      limpiarFiltros,
      cambiarPagina,
      verDetallesReporte,
      eliminarReporte,
      onReporteGenerado,
      formatearFecha,
      cleanup
    }
  },
  beforeUnmount() {
    this.cleanup()
  }
}
</script>

<style scoped>
.reports-management {
  padding: 1rem;
}

.stats-card {
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease-in-out;
}

.stats-card:hover {
  transform: translateY(-2px);
}

.card {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #374151;
}

.badge {
  font-size: 0.75rem;
}

.btn-group .btn {
  margin-right: 0.25rem;
}

.btn-group .btn:last-child {
  margin-right: 0;
}

.modal-backdrop {
  background-color: rgba(0, 0, 0, 0.5);
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.gap-2 {
  gap: 0.5rem;
}
</style>

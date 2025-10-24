<template>
  <div class="report-management">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="fas fa-chart-bar"></i>
          Gestión de Reportes
        </h1>
        <div class="header-actions">
          <button 
            class="btn btn-primary"
            @click="openCreateModal"
          >
            <i class="fas fa-plus"></i>
            Nuevo Reporte
          </button>
        </div>
      </div>
    </div>

    <!-- Filtros y Búsqueda -->
    <div class="filters-section">
      <div class="filters-row">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="Buscar reportes..."
            @input="debouncedSearch"
          >
        </div>
        
        <div class="filter-group">
          <select v-model="typeFilter" @change="applyFilters">
            <option value="">Todos los tipos</option>
            <option value="calidad">Calidad</option>
            <option value="finca">Finca</option>
            <option value="lote">Lote</option>
            <option value="usuario">Usuario</option>
            <option value="auditoria">Auditoría</option>
            <option value="personalizado">Personalizado</option>
          </select>
        </div>

        <div class="filter-group">
          <select v-model="formatFilter" @change="applyFilters">
            <option value="">Todos los formatos</option>
            <option value="pdf">PDF</option>
            <option value="excel">Excel</option>
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
          </select>
        </div>

        <div class="filter-group">
          <select v-model="statusFilter" @change="applyFilters">
            <option value="">Todos los estados</option>
            <option value="generando">Generando</option>
            <option value="completado">Completado</option>
            <option value="fallido">Fallido</option>
            <option value="expirado">Expirado</option>
          </select>
        </div>

        <div class="filter-group">
          <select v-model="sortBy" @change="applyFilters">
            <option value="-fecha_solicitud">Más recientes</option>
            <option value="fecha_solicitud">Más antiguos</option>
            <option value="titulo">Título</option>
            <option value="tipo_reporte">Tipo</option>
            <option value="formato">Formato</option>
          </select>
        </div>

        <button 
          class="btn btn-outline-secondary"
          @click="clearFilters"
        >
          <i class="fas fa-times"></i>
          Limpiar
        </button>
      </div>
    </div>

    <!-- Estadísticas Rápidas -->
    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-number">{{ totalReports }}</div>
        <div class="stat-label">Total Reportes</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ completedReports }}</div>
        <div class="stat-label">Completados</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ generatingReports }}</div>
        <div class="stat-label">Generando</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ failedReports }}</div>
        <div class="stat-label">Fallidos</div>
      </div>
    </div>

    <!-- Tabla de Reportes -->
    <div class="table-container">
      <div class="table-header">
        <h3>Lista de Reportes</h3>
        <div class="table-actions">
          <button 
            class="btn btn-sm btn-outline-primary"
            @click="exportReports"
            :disabled="loading"
          >
            <i class="fas fa-download"></i>
            Exportar Lista
          </button>
          <button 
            class="btn btn-sm btn-outline-warning"
            @click="cleanupExpired"
            :disabled="loading"
          >
            <i class="fas fa-trash"></i>
            Limpiar Expirados
          </button>
        </div>
      </div>

      <div class="table-body">
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Cargando reportes...</p>
        </div>

        <div v-else-if="reports.length === 0" class="empty-state">
          <i class="fas fa-chart-bar"></i>
          <h3>No se encontraron reportes</h3>
          <p>No hay reportes que coincidan con los filtros aplicados.</p>
        </div>

        <table v-else class="table">
          <thead>
            <tr>
              <th>
                <input 
                  type="checkbox" 
                  v-model="selectAll"
                  @change="toggleSelectAll"
                >
              </th>
              <th>Título</th>
              <th>Tipo</th>
              <th>Formato</th>
              <th>Estado</th>
              <th>Solicitado</th>
              <th>Generado</th>
              <th>Tamaño</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="report in reports" :key="report.id" :class="{ selected: selectedReports.includes(report.id) }">
              <td>
                <input 
                  type="checkbox" 
                  :value="report.id"
                  v-model="selectedReports"
                >
              </td>
              <td>
                <div class="report-info">
                  <strong>{{ report.titulo }}</strong>
                  <small v-if="report.descripcion">{{ report.descripcion }}</small>
                </div>
              </td>
              <td>
                <span class="badge" :class="getTypeBadgeClass(report.tipo_reporte)">
                  {{ report.tipo_reporte_display }}
                </span>
              </td>
              <td>
                <span class="format-badge" :class="getFormatClass(report.formato)">
                  <i :class="getFormatIcon(report.formato)"></i>
                  {{ report.formato_display }}
                </span>
              </td>
              <td>
                <span class="badge" :class="getStatusBadgeClass(report.estado)">
                  <i :class="getStatusIcon(report.estado)"></i>
                  {{ report.estado_display }}
                </span>
              </td>
              <td>
                <span class="date-info">
                  {{ formatDateTime(report.fecha_solicitud) }}
                </span>
              </td>
              <td>
                <span v-if="report.fecha_generacion" class="date-info">
                  {{ formatDateTime(report.fecha_generacion) }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td>
                <span v-if="report.tamaño_archivo_mb" class="size-info">
                  {{ report.tamaño_archivo_mb }} MB
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    class="btn btn-sm btn-outline-primary"
                    @click="viewReport(report)"
                    title="Ver detalles"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                  <button 
                    v-if="report.estado === 'completado' && !report.esta_expirado"
                    class="btn btn-sm btn-outline-success"
                    @click="downloadReport(report)"
                    title="Descargar"
                  >
                    <i class="fas fa-download"></i>
                  </button>
                  <button 
                    v-if="report.estado === 'fallido'"
                    class="btn btn-sm btn-outline-warning"
                    @click="retryReport(report)"
                    title="Reintentar"
                  >
                    <i class="fas fa-redo"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="confirmDeleteReport(report)"
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
      <div v-if="totalPages > 1" class="pagination-container">
        <nav aria-label="Paginación de reportes">
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
    </div>

    <!-- Acciones Masivas -->
    <div v-if="selectedReports.length > 0" class="bulk-actions">
      <div class="bulk-actions-content">
        <span class="selected-count">
          {{ selectedReports.length }} reporte(s) seleccionado(s)
        </span>
        <div class="bulk-buttons">
          <button 
            class="btn btn-sm btn-danger"
            @click="bulkDelete"
          >
            <i class="fas fa-trash"></i>
            Eliminar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Crear Reporte -->
    <ReportGeneratorModal
      v-if="showCreateModal"
      @close="closeCreateModal"
      @created="handleReportCreated"
    />

    <!-- Modal de Detalles de Reporte -->
    <ReportDetailsModal
      v-if="showDetailsModal"
      :report="viewingReport"
      @close="closeDetailsModal"
      @download="downloadReport"
      @retry="retryReport"
    />

    <!-- Modal de Vista Previa -->
    <ReportViewerModal
      v-if="showViewerModal"
      :report="viewingReport"
      @close="closeViewerModal"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import Swal from 'sweetalert2'
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'
import ReportGeneratorModal from '@/components/reports/ReportGeneratorModal.vue'
import ReportDetailsModal from '@/components/reports/ReportDetailsModal.vue'
import ReportViewerModal from '@/components/reports/ReportViewerModal.vue'
import { debounce } from 'lodash-es'

export default {
  name: 'ReportManagement',
  components: {
    ReportGeneratorModal,
    ReportDetailsModal,
    ReportViewerModal
  },
  setup() {
    const router = useRouter()
    const adminStore = useAdminStore()
    const authStore = useAuthStore()

    // Reactive data
    const loading = ref(false)
    const reports = ref([])
    const selectedReports = ref([])
    const selectAll = ref(false)
    
    // Filters and search
    const searchQuery = ref('')
    const typeFilter = ref('')
    const formatFilter = ref('')
    const statusFilter = ref('')
    const sortBy = ref('-fecha_solicitud')
    
    // Pagination
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalReports = ref(0)
    const totalPages = ref(0)
    
    // Modals
    const showCreateModal = ref(false)
    const showDetailsModal = ref(false)
    const showViewerModal = ref(false)
    const viewingReport = ref(null)

    // Computed
    const completedReports = computed(() => 
      reports.value.filter(report => report.estado === 'completado').length
    )
    
    const generatingReports = computed(() => 
      reports.value.filter(report => report.estado === 'generando').length
    )
    
    const failedReports = computed(() => 
      reports.value.filter(report => report.estado === 'fallido').length
    )
    
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
    const loadReports = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          page_size: pageSize.value,
          search: searchQuery.value,
          tipo_reporte: typeFilter.value,
          formato: formatFilter.value,
          estado: statusFilter.value,
          ordering: sortBy.value
        }
        
        const response = await adminStore.getAllReports(params)
        reports.value = response.data.results
        totalReports.value = response.data.count
        totalPages.value = Math.ceil(response.data.count / pageSize.value)
        
      } catch (error) {
        console.error('Error loading reports:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron cargar los reportes'
        })
      } finally {
        loading.value = false
      }
    }

    const debouncedSearch = debounce(() => {
      currentPage.value = 1
      loadReports()
    }, 500)

    const applyFilters = () => {
      currentPage.value = 1
      loadReports()
    }

    const clearFilters = () => {
      searchQuery.value = ''
      typeFilter.value = ''
      formatFilter.value = ''
      statusFilter.value = ''
      sortBy.value = '-fecha_solicitud'
      currentPage.value = 1
      loadReports()
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadReports()
      }
    }

    const toggleSelectAll = () => {
      if (selectAll.value) {
        selectedReports.value = reports.value.map(report => report.id)
      } else {
        selectedReports.value = []
      }
    }

    const openCreateModal = () => {
      showCreateModal.value = true
    }

    const closeCreateModal = () => {
      showCreateModal.value = false
    }

    const viewReport = (report) => {
      viewingReport.value = report
      showDetailsModal.value = true
    }

    const closeDetailsModal = () => {
      showDetailsModal.value = false
      viewingReport.value = null
    }

    const closeViewerModal = () => {
      showViewerModal.value = false
      viewingReport.value = null
    }

    const handleReportCreated = () => {
      closeCreateModal()
      loadReports()
    }

    const downloadReport = async (report) => {
      try {
        const response = await adminStore.downloadReport(report.id)
        
        // Create download link
        const blob = new Blob([response.data], { 
          type: getMimeType(report.formato)
        })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${report.titulo}.${report.formato}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        Swal.fire({
          icon: 'success',
          title: 'Descarga exitosa',
          text: 'El reporte ha sido descargado exitosamente'
        })
        
      } catch (error) {
        console.error('Error downloading report:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo descargar el reporte'
        })
      }
    }

    const retryReport = async (report) => {
      try {
        await adminStore.createReport({
          tipo_reporte: report.tipo_reporte,
          formato: report.formato,
          titulo: report.titulo,
          descripcion: report.descripcion,
          parametros: report.parametros,
          filtros: report.filtros_aplicados
        })
        
        Swal.fire({
          icon: 'success',
          title: 'Reporte reintentado',
          text: 'El reporte ha sido enviado para generación nuevamente'
        })
        
        loadReports()
        
      } catch (error) {
        console.error('Error retrying report:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo reintentar el reporte'
        })
      }
    }

    const confirmDeleteReport = async (report) => {
      const result = await Swal.fire({
        title: '¿Eliminar reporte?',
        text: `¿Estás seguro de que quieres eliminar el reporte "${report.titulo}"?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      })

      if (result.isConfirmed) {
        await deleteReport(report.id)
      }
    }

    const deleteReport = async (reportId) => {
      try {
        await adminStore.deleteReport(reportId)
        
        // Remove from local state
        reports.value = reports.value.filter(report => report.id !== reportId)
        selectedReports.value = selectedReports.value.filter(id => id !== reportId)
        totalReports.value--
        
        Swal.fire({
          icon: 'success',
          title: 'Reporte eliminado',
          text: 'El reporte ha sido eliminado exitosamente'
        })
        
      } catch (error) {
        console.error('Error deleting report:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo eliminar el reporte'
        })
      }
    }

    const bulkDelete = async () => {
      const result = await Swal.fire({
        title: '¿Eliminar reportes?',
        text: `¿Estás seguro de que quieres eliminar ${selectedReports.value.length} reportes?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      })

      if (result.isConfirmed) {
        try {
          const promises = selectedReports.value.map(reportId => 
            adminStore.deleteReport(reportId)
          )
          
          await Promise.all(promises)
          
          // Remove from local state
          reports.value = reports.value.filter(report => 
            !selectedReports.value.includes(report.id)
          )
          
          totalReports.value -= selectedReports.value.length
          selectedReports.value = []
          selectAll.value = false
          
          Swal.fire({
            icon: 'success',
            title: 'Reportes eliminados',
            text: 'Los reportes seleccionados han sido eliminados'
          })
          
        } catch (error) {
          console.error('Error bulk deleting reports:', error)
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudieron eliminar algunos reportes'
          })
        }
      }
    }

    const exportReports = async () => {
      try {
        const response = await adminStore.exportData('reports', 'excel', {
          search: searchQuery.value,
          tipo_reporte: typeFilter.value,
          formato: formatFilter.value,
          estado: statusFilter.value
        })
        
        // Create download link
        const blob = new Blob([response.data], { 
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
        })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `reportes_${new Date().toISOString().split('T')[0]}.xlsx`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        Swal.fire({
          icon: 'success',
          title: 'Exportación exitosa',
          text: 'La lista de reportes ha sido exportada exitosamente'
        })
        
      } catch (error) {
        console.error('Error exporting reports:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo exportar la lista de reportes'
        })
      }
    }

    const cleanupExpired = async () => {
      const result = await Swal.fire({
        title: '¿Limpiar reportes expirados?',
        text: 'Esta acción eliminará todos los reportes expirados del sistema.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, limpiar',
        cancelButtonText: 'Cancelar'
      })

      if (result.isConfirmed) {
        try {
          const response = await adminStore.cleanupExpiredReports()
          
          Swal.fire({
            icon: 'success',
            title: 'Limpieza completada',
            text: `Se limpiaron ${response.data.cleaned_count} reportes expirados`
          })
          
          loadReports()
          
        } catch (error) {
          console.error('Error cleaning up expired reports:', error)
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudieron limpiar los reportes expirados'
          })
        }
      }
    }

    // Utility methods
    const formatDateTime = (date) => {
      return new Date(date).toLocaleString('es-ES')
    }

    const getMimeType = (format) => {
      const mimeTypes = {
        'pdf': 'application/pdf',
        'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'csv': 'text/csv',
        'json': 'application/json'
      }
      return mimeTypes[format] || 'application/octet-stream'
    }

    const getTypeBadgeClass = (type) => {
      const classes = {
        'calidad': 'badge-success',
        'finca': 'badge-info',
        'lote': 'badge-primary',
        'usuario': 'badge-warning',
        'auditoria': 'badge-danger',
        'personalizado': 'badge-secondary'
      }
      return classes[type] || 'badge-secondary'
    }

    const getFormatClass = (format) => {
      const classes = {
        'pdf': 'format-pdf',
        'excel': 'format-excel',
        'csv': 'format-csv',
        'json': 'format-json'
      }
      return classes[format] || 'format-default'
    }

    const getFormatIcon = (format) => {
      const icons = {
        'pdf': 'fas fa-file-pdf',
        'excel': 'fas fa-file-excel',
        'csv': 'fas fa-file-csv',
        'json': 'fas fa-file-code'
      }
      return icons[format] || 'fas fa-file'
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        'generando': 'badge-warning',
        'completado': 'badge-success',
        'fallido': 'badge-danger',
        'expirado': 'badge-secondary'
      }
      return classes[status] || 'badge-secondary'
    }

    const getStatusIcon = (status) => {
      const icons = {
        'generando': 'fas fa-spinner fa-spin',
        'completado': 'fas fa-check',
        'fallido': 'fas fa-times',
        'expirado': 'fas fa-clock'
      }
      return icons[status] || 'fas fa-circle'
    }

    // Watchers
    watch(selectedReports, (newValue) => {
      selectAll.value = newValue.length === reports.value.length && reports.value.length > 0
    })

    // Lifecycle
    onMounted(() => {
      // Verificar permisos de administrador
      if (!authStore.user?.is_superuser && !authStore.user?.is_staff) {
        router.push('/unauthorized')
        return
      }

      loadReports()
    })

    return {
      // Data
      loading,
      reports,
      selectedReports,
      selectAll,
      searchQuery,
      typeFilter,
      formatFilter,
      statusFilter,
      sortBy,
      currentPage,
      totalReports,
      totalPages,
      showCreateModal,
      showDetailsModal,
      showViewerModal,
      viewingReport,
      
      // Computed
      completedReports,
      generatingReports,
      failedReports,
      visiblePages,
      
      // Methods
      loadReports,
      debouncedSearch,
      applyFilters,
      clearFilters,
      changePage,
      toggleSelectAll,
      openCreateModal,
      closeCreateModal,
      viewReport,
      closeDetailsModal,
      closeViewerModal,
      handleReportCreated,
      downloadReport,
      retryReport,
      confirmDeleteReport,
      bulkDelete,
      exportReports,
      cleanupExpired,
      formatDateTime,
      getTypeBadgeClass,
      getFormatClass,
      getFormatIcon,
      getStatusBadgeClass,
      getStatusIcon
    }
  }
}
</script>

<style scoped>
.report-management {
  padding: 20px;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.page-header {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0;
  color: #2c3e50;
  font-size: 1.8rem;
}

.page-title i {
  margin-right: 10px;
  color: #3498db;
}

.filters-section {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filters-row {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #7f8c8d;
}

.search-box input {
  width: 100%;
  padding: 10px 10px 10px 35px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
}

.filter-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  min-width: 150px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  background: white;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.table-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.table-header {
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-header h3 {
  margin: 0;
  color: #2c3e50;
}

.table-body {
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

.table {
  margin: 0;
  width: 100%;
}

.table th {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  font-weight: 600;
  color: #495057;
  padding: 15px;
}

.table td {
  padding: 15px;
  border-bottom: 1px solid #dee2e6;
}

.table tbody tr:hover {
  background-color: #f8f9fa;
}

.table tbody tr.selected {
  background-color: #e3f2fd;
}

.report-info strong {
  display: block;
  color: #2c3e50;
  font-size: 0.9rem;
}

.report-info small {
  color: #7f8c8d;
  font-size: 0.8rem;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.badge-success {
  background-color: #d4edda;
  color: #155724;
}

.badge-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.badge-warning {
  background-color: #fff3cd;
  color: #856404;
}

.badge-info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.badge-primary {
  background-color: #cce5ff;
  color: #004085;
}

.badge-secondary {
  background-color: #e2e3e5;
  color: #383d41;
}

.format-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.format-pdf {
  background-color: #f8d7da;
  color: #721c24;
}

.format-excel {
  background-color: #d4edda;
  color: #155724;
}

.format-csv {
  background-color: #d1ecf1;
  color: #0c5460;
}

.format-json {
  background-color: #fff3cd;
  color: #856404;
}

.format-default {
  background-color: #e2e3e5;
  color: #383d41;
}

.date-info {
  font-size: 0.8rem;
  color: #495057;
}

.size-info {
  font-size: 0.8rem;
  color: #495057;
  font-weight: 500;
}

.text-muted {
  color: #7f8c8d;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.action-buttons .btn {
  padding: 5px 8px;
  font-size: 0.8rem;
}

.pagination-container {
  padding: 20px;
  display: flex;
  justify-content: center;
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
  color: #2980b9;
  background-color: #e9ecef;
  border-color: #dee2e6;
}

.bulk-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 10px;
  padding: 15px 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
}

.bulk-actions-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.selected-count {
  font-weight: 500;
  color: #2c3e50;
}

.bulk-buttons {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>

<template>
  <div class="bg-gray-50 min-h-screen">
    <!-- Sidebar -->
    <AdminSidebar 
      :brand-name="brandName"
      :user-name="userName"
      :user-role="userRole"
      :current-route="$route.path"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
    />
    
    <!-- Contenido principal -->
    <div class="p-4 sm:ml-64">
      <div class="p-4 mt-14">
        <!-- Botones de acción superiores -->
        <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between mb-6">
          <div class="flex gap-2">
            <button
              @click="showFilters = !showFilters"
              class="px-4 py-2 text-sm font-medium rounded-lg border transition-colors"
              :class="showFilters ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'"
            >
              <i class="fas fa-filter mr-2"></i>
              {{ showFilters ? 'Ocultar Filtros' : 'Mostrar Filtros' }}
            </button>
            <button
              @click="openReportGenerator"
              class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
            >
              <i class="fas fa-plus mr-2"></i>
              Nuevo Reporte
            </button>
          </div>
        </div>
        
        <!-- Contenido principal -->
        <main class="space-y-6">
          <!-- Tarjetas de estadísticas -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-4 md:mb-6">
            <StatsCard 
              title="Total de Reportes"
              :value="stats.totalReports"
              :change="stats.reportsChange"
              icon="DocumentTextIcon"
              variant="info"
            />
            <StatsCard 
              title="Reportes Completados"
              :value="stats.completedReports"
              :change="stats.completedChange"
              icon="CheckCircleIcon"
              variant="success"
            />
            <StatsCard 
              title="En Proceso"
              :value="stats.inProgressReports"
              :change="stats.inProgressChange"
              icon="ClockIcon"
              variant="warning"
            />
            <StatsCard 
              title="Con Errores"
              :value="stats.errorReports"
              :change="stats.errorChange"
              icon="ExclamationTriangleIcon"
              variant="danger"
            />
          </div>

          <!-- Panel de filtros avanzados -->
          <div v-if="showFilters" class="bg-white rounded-lg shadow-sm border border-gray-200 mb-6 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">
                <i class="fas fa-filter mr-2 text-blue-600"></i>
                Filtros Avanzados
              </h3>
              <button
                @click="clearFilters"
                class="text-sm text-gray-500 hover:text-gray-700"
              >
                <i class="fas fa-times mr-1"></i>
                Limpiar Filtros
              </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              <!-- Filtro por tipo de reporte -->
              <div class="form-group">
                <label for="report-filter-tipo" class="form-label">Tipo de Reporte</label>
                <select id="report-filter-tipo" v-model="filters.tipo_reporte" class="form-select">
                  <option value="">Todos los tipos</option>
                  <option value="calidad">Reporte de Calidad</option>
                  <option value="finca">Reporte de Finca</option>
                  <option value="lote">Reporte de Lote</option>
                  <option value="usuario">Reporte de Usuario</option>
                  <option value="auditoria">Reporte de Auditoría</option>
                  <option value="personalizado">Reporte Personalizado</option>
                </select>
              </div>

              <!-- Filtro por formato -->
              <div class="form-group">
                <label for="report-filter-formato" class="form-label">Formato</label>
                <select id="report-filter-formato" v-model="filters.formato" class="form-select">
                  <option value="">Todos los formatos</option>
                  <option value="pdf">PDF</option>
                  <option value="excel">Excel</option>
                  <option value="csv">CSV</option>
                  <option value="json">JSON</option>
                </select>
              </div>

              <!-- Filtro por estado -->
              <div class="form-group">
                <label for="report-filter-estado" class="form-label">Estado</label>
                <select id="report-filter-estado" v-model="filters.estado" class="form-select">
                  <option value="">Todos los estados</option>
                  <option value="pendiente">Pendiente</option>
                  <option value="procesando">Procesando</option>
                  <option value="completado">Completado</option>
                  <option value="error">Error</option>
                </select>
              </div>

              <!-- Filtro por usuario -->
              <div class="form-group">
                <label for="report-filter-usuario" class="form-label">Usuario</label>
                <select id="report-filter-usuario" v-model="filters.usuario_id" class="form-select">
                  <option value="">Todos los usuarios</option>
                  <option v-for="user in users" :key="user.id" :value="user.id">
                    {{ user.first_name }} {{ user.last_name }}
                  </option>
                </select>
              </div>

              <!-- Filtro por fecha desde -->
              <div class="form-group">
                <label for="report-filter-fecha-desde" class="form-label">Fecha Desde</label>
                <input
                  id="report-filter-fecha-desde"
                  type="date"
                  v-model="filters.fecha_desde"
                  class="form-input"
                />
              </div>

              <!-- Filtro por fecha hasta -->
              <div class="form-group">
                <label for="report-filter-fecha-hasta" class="form-label">Fecha Hasta</label>
                <input
                  id="report-filter-fecha-hasta"
                  type="date"
                  v-model="filters.fecha_hasta"
                  class="form-input"
                />
              </div>

              <!-- Filtro por finca -->
              <div class="form-group">
                <label for="report-filter-finca" class="form-label">Finca</label>
                <select id="report-filter-finca" v-model="filters.finca_id" class="form-select">
                  <option value="">Todas las fincas</option>
                  <option v-for="finca in fincas" :key="finca.id" :value="finca.id">
                    {{ finca.nombre }}
                  </option>
                </select>
              </div>

              <!-- Filtro por lote -->
              <div class="form-group">
                <label for="report-filter-lote" class="form-label">Lote</label>
                <select id="report-filter-lote" v-model="filters.lote_id" class="form-select">
                  <option value="">Todos los lotes</option>
                  <option v-for="lote in lotes" :key="lote.id" :value="lote.id">
                    {{ lote.identificador }} - {{ lote.variedad }}
                  </option>
                </select>
              </div>
            </div>

            <!-- Botones de acción de filtros -->
            <div class="flex justify-end gap-2 mt-4 pt-4 border-t border-gray-200">
              <button
                @click="applyFilters"
                class="btn btn-primary"
                :disabled="loading"
              >
                <i class="fas fa-search mr-2"></i>
                Aplicar Filtros
              </button>
              <button
                @click="exportFiltered"
                class="btn btn-outline"
                :disabled="loading || filteredReports.length === 0"
              >
                <i class="fas fa-download mr-2"></i>
                Exportar Resultados
              </button>
            </div>
          </div>

          <!-- Controles principales -->
          <div class="mb-4 md:mb-6">
            <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
              <!-- Selector de período rápido -->
              <div class="flex gap-4">
                <PeriodSelector 
                  v-model="selectedPeriod"
                  :options="periodOptions"
                  @update:model-value="handlePeriodChange"
                />
                
                <!-- Selector de vista -->
                <div class="form-group">
                  <select v-model="viewMode" class="form-select">
                    <option value="table">Vista de Tabla</option>
                    <option value="cards">Vista de Tarjetas</option>
                    <option value="timeline">Vista de Cronología</option>
                  </select>
                </div>
              </div>
              
              <!-- Botones de acción -->
              <div class="flex gap-2">
                <button
                  @click="refreshReports"
                  class="btn btn-outline"
                  :disabled="loading"
                >
                  <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
                  Actualizar
                </button>
                <button
                  @click="bulkExport"
                  class="btn btn-outline"
                  :disabled="loading || selectedReports.length === 0"
                >
                  <i class="fas fa-download mr-2"></i>
                  Exportar Seleccionados ({{ selectedReports.length }})
                </button>
                <button
                  @click="bulkDelete"
                  class="btn btn-danger"
                  :disabled="loading || selectedReports.length === 0"
                >
                  <i class="fas fa-trash mr-2"></i>
                  Eliminar Seleccionados
                </button>
              </div>
            </div>
          </div>
          
          <!-- Vista de tabla -->
          <div v-if="viewMode === 'table'" class="flex-1 min-h-0">
            <ReportsTable 
              :reports="filteredReports"
              :loading="loading"
              :selected-reports="selectedReports"
              @view="handleViewReport"
              @download="handleDownloadReport"
              @delete="handleDeleteReport"
              @sort="handleSort"
              @select="handleSelectReport"
              @select-all="handleSelectAll"
            />
          </div>

          <!-- Vista de tarjetas -->
          <div v-else-if="viewMode === 'cards'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <ReportCard
              v-for="report in filteredReports"
              :key="report.id"
              :report="report"
              :selected="selectedReports.includes(report.id)"
              @view="handleViewReport"
              @download="handleDownloadReport"
              @delete="handleDeleteReport"
              @select="handleSelectReport"
            />
          </div>

          <!-- Vista de cronología -->
          <div v-else-if="viewMode === 'timeline'" class="flex-1 min-h-0">
            <ReportsTimeline
              :reports="filteredReports"
              :loading="loading"
              @view="handleViewReport"
              @download="handleDownloadReport"
            />
          </div>

          <!-- Paginación -->
          <div v-if="pagination.totalPages > 1" class="mt-6">
            <Pagination
              :current-page="pagination.currentPage"
              :total-pages="pagination.totalPages"
              :total-items="pagination.totalItems"
              :items-per-page="pagination.itemsPerPage"
              @page-change="handlePageChange"
            />
          </div>
        </main>
      </div>
    </div>

    <!-- Modal de generación de reportes -->
    <ReportGeneratorModal
      v-if="showReportGenerator"
      @close="showReportGenerator = false"
      @created="handleReportCreated"
    />

    <!-- Modal de vista previa de reporte -->
    <ReportPreviewModal
      v-if="showReportPreview"
      :report="selectedReport"
      @close="showReportPreview = false"
      @download="handleDownloadReport"
    />

    <!-- Modal de confirmación de eliminación -->
    <ConfirmModal
      v-if="showDeleteConfirm"
      title="Confirmar Eliminación"
      :message="deleteConfirmMessage"
      @confirm="confirmDelete"
      @cancel="showDeleteConfirm = false"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import AdminSidebar from '@/components/layout/Common/Sidebar.vue';
import PeriodSelector from '@/components/reportes/PeriodSelector.vue';
import StatsCard from '@/components/reportes/StatsCard.vue';
import ReportsTable from '@/components/reportes/ReportsTable.vue';
import ReportCard from '@/components/reportes/ReportCard.vue';
import ReportsTimeline from '@/components/reportes/ReportsTimeline.vue';
import Pagination from '@/components/common/Pagination.vue';
import ReportGeneratorModal from '@/components/reports/ReportGeneratorModal.vue';
import ReportPreviewModal from '@/components/reports/ReportPreviewModal.vue';
import ConfirmModal from '@/components/common/ConfirmModal.vue';
import { useReportsStore } from '@/stores/reports';
import { useAuthStore } from '@/stores/auth';
import { usePagination } from '@/composables/usePagination';
import Swal from 'sweetalert2';

export default {
  name: 'Reportes',
  components: {
    AdminSidebar,
    PeriodSelector,
    StatsCard,
    ReportsTable,
    ReportCard,
    ReportsTimeline,
    Pagination,
    ReportGeneratorModal,
    ReportPreviewModal,
    ConfirmModal
  },
  setup() {
    const router = useRouter();
    const reportsStore = useReportsStore();
    const authStore = useAuthStore();

    // Estado reactivo
    const loading = ref(false);
    const showFilters = ref(false);
    const showReportGenerator = ref(false);
    const showReportPreview = ref(false);
    const showDeleteConfirm = ref(false);
    const viewMode = ref('table');
    const selectedPeriod = ref('month');
    const selectedReports = ref([]);
    const selectedReport = ref(null);
    const deleteConfirmMessage = ref('');
    const pendingDeleteId = ref(null);

    // Props para AdminSidebar y AdminNavbar
    const brandName = computed(() => 'CacaoScan');
    
    const userName = computed(() => {
      const user = authStore.user;
      if (user?.first_name && user?.last_name) {
        return `${user.first_name} ${user.last_name}`;
      }
      return user?.username || 'Usuario';
    });

    const userRole = computed(() => {
      return authStore.user?.is_superuser ? 'Administrador' : 'Analista';
    });

    const navbarTitle = ref('Reportes');
    const navbarSubtitle = ref('Genera y gestiona reportes de análisis');
    const searchPlaceholder = ref('Buscar reportes...');
    const refreshButtonText = ref('Actualizar');

    // Opciones del selector de período
    const periodOptions = [
      { value: 'week', label: 'Esta Semana' },
      { value: 'month', label: 'Este Mes' },
      { value: 'quarter', label: 'Este Trimestre' },
      { value: 'year', label: 'Este Año' },
      { value: 'custom', label: 'Personalizado' }
    ];

    // Filtros
    const filters = ref({
      tipo_reporte: '',
      formato: '',
      estado: '',
      usuario_id: '',
      fecha_desde: '',
      fecha_hasta: '',
      finca_id: '',
      lote_id: ''
    });

    // Datos para filtros
    const users = ref([]);
    const fincas = ref([]);
    const lotes = ref([]);

    // Estadísticas
    const stats = computed(() => reportsStore.stats);

    // Reportes filtrados
    const filteredReports = computed(() => {
      let reports = reportsStore.reports;

      // Aplicar filtros
      if (filters.value.tipo_reporte) {
        reports = reports.filter(r => r.tipo_reporte === filters.value.tipo_reporte);
      }
      if (filters.value.formato) {
        reports = reports.filter(r => r.formato === filters.value.formato);
      }
      if (filters.value.estado) {
        reports = reports.filter(r => r.estado === filters.value.estado);
      }
      if (filters.value.usuario_id) {
        reports = reports.filter(r => r.usuario_id === Number.parseInt(filters.value.usuario_id));
      }
      if (filters.value.fecha_desde) {
        reports = reports.filter(r => new Date(r.fecha_solicitud) >= new Date(filters.value.fecha_desde));
      }
      if (filters.value.fecha_hasta) {
        reports = reports.filter(r => new Date(r.fecha_solicitud) <= new Date(filters.value.fecha_hasta));
      }
      if (filters.value.finca_id) {
        reports = reports.filter(r => r.parametros?.finca_id === Number.parseInt(filters.value.finca_id));
      }
      if (filters.value.lote_id) {
        reports = reports.filter(r => r.parametros?.lote_id === Number.parseInt(filters.value.lote_id));
      }

      return reports;
    });

    // Paginación - using composable
    const paginationComposable = usePagination({
      initialPage: 1,
      initialItemsPerPage: 20
    });

    // Sync composable with store pagination
    watch(() => reportsStore.pagination, (storePagination) => {
      if (storePagination) {
        paginationComposable.updateFromApiResponse({
          page: storePagination.currentPage,
          page_size: storePagination.itemsPerPage,
          count: storePagination.totalItems,
          total_pages: storePagination.totalPages
        });
      }
    }, { immediate: true });

    // Computed pagination for component (backward compatibility)
    const pagination = computed(() => ({
      currentPage: paginationComposable.currentPage.value,
      totalPages: paginationComposable.totalPages.value,
      totalItems: paginationComposable.totalItems.value,
      itemsPerPage: paginationComposable.itemsPerPage.value
    }));

    // Métodos para AdminSidebar y AdminNavbar
    const handleMenuClick = (menuItem) => {
      if (menuItem.route) {
        router.push(menuItem.route);
      }
    };

    const handleLogout = async () => {
      try {
        await authStore.logout();
        router.push('/login');
      } catch (error) {
        console.error('Error al cerrar sesión:', error);
      }
    };

    const handleSearch = (query) => {
      filters.value.search = query;
      applyFilters();
    };

    const handleRefresh = async () => {
      await loadInitialData();
      Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'success',
        title: 'Datos actualizados',
        showConfirmButton: false,
        timer: 2000
      });
    };

    const loadInitialData = async () => {
      try {
        loading.value = true;
        await Promise.all([
          reportsStore.fetchReports(),
          reportsStore.fetchStats(),
          loadUsers(),
          loadFincas()
        ]);
      } catch (error) {
        console.error('Error loading initial data:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron cargar los datos iniciales'
        });
      } finally {
        loading.value = false;
      }
    };

    const loadUsers = async () => {
      try {
        const response = await reportsStore.fetchUsers();
        users.value = response.data.results || [];
      } catch (error) {
        console.error('Error loading users:', error);
      }
    };

    const loadFincas = async () => {
      try {
        const response = await reportsStore.fetchFincas();
        fincas.value = response.data.results || [];
      } catch (error) {
        console.error('Error loading fincas:', error);
      }
    };

    const loadLotes = async (fincaId) => {
      if (!fincaId) {
        lotes.value = [];
        return;
      }
      try {
        const response = await reportsStore.fetchLotesByFinca(fincaId);
        lotes.value = response.data.results || [];
      } catch (error) {
        console.error('Error loading lotes:', error);
        lotes.value = [];
      }
    };

    const handlePeriodChange = async (period) => {
      selectedPeriod.value = period;
      await applyFilters();
    };

    const applyFilters = async () => {
      try {
        loading.value = true;
        await reportsStore.fetchReports({
          ...filters.value,
          period: selectedPeriod.value
        });
      } catch (error) {
        console.error('Error applying filters:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron aplicar los filtros'
        });
      } finally {
        loading.value = false;
      }
    };

    const clearFilters = () => {
      filters.value = {
        tipo_reporte: '',
        formato: '',
        estado: '',
        usuario_id: '',
        fecha_desde: '',
        fecha_hasta: '',
        finca_id: '',
        lote_id: ''
      };
      selectedPeriod.value = 'month';
      applyFilters();
    };

    const openReportGenerator = () => {
      showReportGenerator.value = true;
    };

    const handleReportCreated = (report) => {
      reportsStore.addReport(report);
      showReportGenerator.value = false;
      Swal.fire({
        icon: 'success',
        title: 'Reporte Creado',
        text: 'El reporte ha sido enviado para generación'
      });
    };

    const handleViewReport = (report) => {
      selectedReport.value = report;
      showReportPreview.value = true;
    };

    const handleDownloadReport = async (report) => {
      try {
        await reportsStore.downloadReport(report.id);
        Swal.fire({
          icon: 'success',
          title: 'Descarga Iniciada',
          text: 'El archivo se está descargando'
        });
      } catch (error) {
        console.error('Error downloading report:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo descargar el reporte'
        });
      }
    };

    const handleDeleteReport = (report) => {
      pendingDeleteId.value = report.id;
      deleteConfirmMessage.value = `¿Estás seguro de que quieres eliminar el reporte "${report.titulo}"?`;
      showDeleteConfirm.value = true;
    };

    const confirmDelete = async () => {
      if (!pendingDeleteId.value) return;

      try {
        await reportsStore.deleteReport(pendingDeleteId.value);
        Swal.fire({
          icon: 'success',
          title: 'Reporte Eliminado',
          text: 'El reporte ha sido eliminado correctamente'
        });
      } catch (error) {
        console.error('Error deleting report:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo eliminar el reporte'
        });
      } finally {
        showDeleteConfirm.value = false;
        pendingDeleteId.value = null;
      }
    };

    const handleSort = async ({ key, order }) => {
      try {
        await reportsStore.fetchReports({
          sort_by: key,
          sort_order: order
        });
      } catch (error) {
        console.error('Error sorting reports:', error);
      }
    };

    const handleSelectReport = (reportId) => {
      const index = selectedReports.value.indexOf(reportId);
      if (index > -1) {
        selectedReports.value.splice(index, 1);
      } else {
        selectedReports.value.push(reportId);
      }
    };

    const handleSelectAll = (checked) => {
      if (checked) {
        selectedReports.value = filteredReports.value.map(r => r.id);
      } else {
        selectedReports.value = [];
      }
    };

    const handlePageChange = async (page) => {
      // Update composable first
      paginationComposable.goToPage(page);
      
      // Then fetch data with new page
      try {
        await reportsStore.fetchReports({ page });
      } catch (error) {
        console.error('Error changing page:', error);
      }
    };

    const refreshReports = async () => {
      await loadInitialData();
    };

    const exportFiltered = async () => {
      try {
        await reportsStore.exportReports({
          ...filters.value,
          format: 'excel'
        });
        Swal.fire({
          icon: 'success',
          title: 'Exportación Iniciada',
          text: 'El archivo se está generando'
        });
      } catch (error) {
        console.error('Error exporting reports:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo exportar los reportes'
        });
      }
    };

    const bulkExport = async () => {
      if (selectedReports.value.length === 0) return;

      try {
        await reportsStore.exportReports({
          report_ids: selectedReports.value,
          format: 'zip'
        });
        Swal.fire({
          icon: 'success',
          title: 'Exportación Iniciada',
          text: 'Los archivos se están generando'
        });
      } catch (error) {
        console.error('Error bulk exporting reports:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo exportar los reportes seleccionados'
        });
      }
    };

    const bulkDelete = async () => {
      if (selectedReports.value.length === 0) return;

      const confirmed = await Swal.fire({
        title: 'Confirmar Eliminación',
        text: `¿Estás seguro de que quieres eliminar ${selectedReports.value.length} reportes?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      });

      if (confirmed.isConfirmed) {
        try {
          await reportsStore.bulkDeleteReports(selectedReports.value);
          selectedReports.value = [];
          Swal.fire({
            icon: 'success',
            title: 'Reportes Eliminados',
            text: 'Los reportes han sido eliminados correctamente'
          });
        } catch (error) {
          console.error('Error bulk deleting reports:', error);
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudieron eliminar los reportes'
          });
        }
      }
    };

    // Watchers
    watch(() => filters.value.finca_id, (newFincaId) => {
      if (newFincaId) {
        loadLotes(newFincaId);
      } else {
        lotes.value = [];
        filters.value.lote_id = '';
      }
    });

    // Lifecycle
    onMounted(() => {
      loadInitialData();
    });

    return {
      // Estado
      loading,
      showFilters,
      showReportGenerator,
      showReportPreview,
      showDeleteConfirm,
      viewMode,
      selectedPeriod,
      selectedReports,
      selectedReport,
      deleteConfirmMessage,

      // Props para componentes
      brandName,
      userName,
      userRole,
      navbarTitle,
      navbarSubtitle,
      searchPlaceholder,
      refreshButtonText,

      // Datos
      periodOptions,
      filters,
      users,
      fincas,
      lotes,
      stats,
      filteredReports,
      pagination,

      // Métodos
      handleMenuClick,
      handleLogout,
      handleSearch,
      handleRefresh,
      handlePeriodChange,
      applyFilters,
      clearFilters,
      openReportGenerator,
      handleReportCreated,
      handleViewReport,
      handleDownloadReport,
      handleDeleteReport,
      confirmDelete,
      handleSort,
      handleSelectReport,
      handleSelectAll,
      handlePageChange,
      refreshReports,
      exportFiltered,
      bulkExport,
      bulkDelete
    };
  }
};
</script>

<style scoped>
/* Estilos específicos para la vista de reportes */
.min-h-screen {
  min-height: 100vh;
}

/* Formularios */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.form-select,
.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Botones */
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
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1e3a8a;
  border-color: #1e3a8a;
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
@media (max-width: 768px) {
  .dashboard-layout {
    flex-direction: column;
  }
  
  .dashboard-content {
    height: calc(100vh - 60px);
  }
  
  .grid {
    grid-template-columns: 1fr;
  }
  
  .flex-col.sm\:flex-row {
    flex-direction: column;
  }
  
  .items-start.sm\:items-center {
    align-items: flex-start;
  }
  
  .justify-between {
    justify-content: flex-start;
  }
  
  .flex.gap-2 {
    margin-top: 1rem;
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 640px) {
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .xl\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

/* Animaciones */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

main {
  animation: fadeIn 0.5s ease-out;
}

/* Estados de carga */
.loading {
  opacity: 0.6;
  pointer-events: none;
}

/* Mejoras para accesibilidad */
*:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Scroll suave */
.overflow-y-auto {
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
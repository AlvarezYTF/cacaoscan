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
              @click="exportAuditData"
              class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
              :disabled="loading"
            >
              <i class="fas fa-download mr-2"></i>
              Exportar
            </button>
          </div>
        </div>
        
        <!-- Contenido principal -->
        <main class="space-y-6">
          <!-- Tarjetas de estadísticas -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-4 md:mb-6">
            <StatsCard 
              title="Actividades Totales"
              :value="stats.activity_log?.total_activities || 0"
              :change="stats.activity_log?.activities_today || 0"
              icon="ActivityIcon"
              variant="info"
              change-label="Hoy"
            />
            <StatsCard 
              title="Logins Exitosos"
              :value="stats.login_history?.successful_logins || 0"
              :change="Math.round(stats.login_history?.success_rate || 0)"
              icon="CheckCircleIcon"
              variant="success"
              change-label="% Éxito"
            />
            <StatsCard 
              title="Logins Fallidos"
              :value="stats.login_history?.failed_logins || 0"
              :change="stats.login_history?.failed_logins || 0"
              icon="ExclamationTriangleIcon"
              variant="warning"
              change-label="Fallos"
            />
            <StatsCard 
              title="Usuarios Activos"
              :value="stats.activity_log?.top_active_users?.length || 0"
              :change="stats.activity_log?.activities_today || 0"
              icon="UsersIcon"
              variant="primary"
              change-label="Hoy"
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
              <!-- Filtro por tipo de auditoría -->
              <div class="form-group">
                <label for="audit-filter-type" class="form-label">Tipo de Auditoría</label>
                <select id="audit-filter-type" v-model="filters.auditType" class="form-select" @change="handleAuditTypeChange">
                  <option value="activity">Logs de Actividad</option>
                  <option value="login">Historial de Logins</option>
                  <option value="both">Ambos</option>
                </select>
              </div>

              <!-- Filtro por usuario -->
              <div class="form-group">
                <label for="audit-filter-usuario" class="form-label">Usuario</label>
                <input
                  id="audit-filter-usuario"
                  type="text"
                  v-model="filters.usuario"
                  placeholder="Nombre de usuario"
                  class="form-input"
                />
              </div>

              <!-- Filtro por acción (solo para activity logs) -->
              <div v-if="filters.auditType === 'activity' || filters.auditType === 'both'" class="form-group">
                <label for="audit-filter-accion" class="form-label">Acción</label>
                <select id="audit-filter-accion" v-model="filters.accion" class="form-select">
                  <option value="">Todas las acciones</option>
                  <option value="login">Inicio de Sesión</option>
                  <option value="logout">Cierre de Sesión</option>
                  <option value="create">Creación</option>
                  <option value="update">Actualización</option>
                  <option value="delete">Eliminación</option>
                  <option value="view">Visualización</option>
                  <option value="download">Descarga</option>
                  <option value="upload">Subida</option>
                  <option value="analysis">Análisis</option>
                  <option value="training">Entrenamiento</option>
                  <option value="report">Reporte</option>
                  <option value="error">Error</option>
                </select>
              </div>

              <!-- Filtro por modelo (solo para activity logs) -->
              <div v-if="filters.auditType === 'activity' || filters.auditType === 'both'" class="form-group">
                <label for="audit-filter-modelo" class="form-label">Modelo</label>
                <input
                  id="audit-filter-modelo"
                  type="text"
                  v-model="filters.modelo"
                  placeholder="Ej: CacaoImage, Finca"
                  class="form-input"
                />
              </div>

              <!-- Filtro por IP -->
              <div class="form-group">
                <label for="audit-filter-ip" class="form-label">Dirección IP</label>
                <input
                  id="audit-filter-ip"
                  type="text"
                  v-model="filters.ip_address"
                  placeholder="192.168.1.1"
                  class="form-input"
                />
              </div>

              <!-- Filtro por éxito (solo para login history) -->
              <div v-if="filters.auditType === 'login' || filters.auditType === 'both'" class="form-group">
                <label for="audit-filter-success" class="form-label">Estado del Login</label>
                <select id="audit-filter-success" v-model="filters.success" class="form-select">
                  <option value="">Todos</option>
                  <option value="true">Exitosos</option>
                  <option value="false">Fallidos</option>
                </select>
              </div>

              <!-- Filtro por fecha desde -->
              <div class="form-group">
                <label for="audit-filter-fecha-desde" class="form-label">Fecha Desde</label>
                <input
                  id="audit-filter-fecha-desde"
                  type="date"
                  v-model="filters.fecha_desde"
                  class="form-input"
                />
              </div>

              <!-- Filtro por fecha hasta -->
              <div class="form-group">
                <label for="audit-filter-fecha-hasta" class="form-label">Fecha Hasta</label>
                <input
                  id="audit-filter-fecha-hasta"
                  type="date"
                  v-model="filters.fecha_hasta"
                  class="form-input"
                />
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
                :disabled="loading"
              >
                <i class="fas fa-download mr-2"></i>
                Exportar Resultados
              </button>
            </div>
          </div>

          <!-- Controles principales -->
          <div class="mb-4 md:mb-6">
            <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
              <!-- Selector de vista -->
              <div class="flex gap-4">
                <div class="form-group">
                  <select v-model="viewMode" class="form-select">
                    <option value="table">Vista de Tabla</option>
                    <option value="timeline">Vista de Cronología</option>
                    <option value="cards">Vista de Tarjetas</option>
                  </select>
                </div>
                
                <!-- Selector de período rápido -->
                <div class="form-group">
                  <select v-model="selectedPeriod" class="form-select" @change="handlePeriodChange">
                    <option value="today">Hoy</option>
                    <option value="week">Esta Semana</option>
                    <option value="month">Este Mes</option>
                    <option value="quarter">Este Trimestre</option>
                    <option value="year">Este Año</option>
                    <option value="custom">Personalizado</option>
                  </select>
                </div>
              </div>
              
              <!-- Botones de acción -->
              <div class="flex gap-2">
                <button
                  @click="toggleRealTime"
                  class="btn"
                  :class="realTimeEnabled ? 'btn-success' : 'btn-outline'"
                >
                  <i class="fas fa-broadcast-tower"></i>
                  {{ realTimeEnabled ? 'Tiempo Real ON' : 'Tiempo Real OFF' }}
                </button>
                <button
                  @click="showStatsModal = true"
                  class="btn btn-outline"
                >
                  <i class="fas fa-chart-bar mr-2"></i>
                  Estadísticas Detalladas
                </button>
              </div>
            </div>
          </div>

          <!-- Vista de tabla -->
          <div v-if="viewMode === 'table'" class="flex-1 min-h-0">
            <AuditTable 
              :data="filteredData"
              :loading="loading"
              :audit-type="filters.auditType"
              @view-details="handleViewDetails"
              @sort="handleSort"
            />
          </div>

          <!-- Vista de cronología -->
          <div v-else-if="viewMode === 'timeline'" class="flex-1 min-h-0">
            <AuditTimeline
              :data="filteredData"
              :loading="loading"
              :audit-type="filters.auditType"
              @view-details="handleViewDetails"
            />
          </div>

          <!-- Vista de tarjetas -->
          <div v-else-if="viewMode === 'cards'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <AuditCard
              v-for="item in filteredData"
              :key="item.id"
              :data="item"
              :audit-type="filters.auditType"
              @view-details="handleViewDetails"
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

    <!-- Modal de detalles de auditoría -->
    <AuditDetailsModal
      v-if="showDetailsModal"
      :data="selectedItem"
      :audit-type="selectedAuditType"
      @close="showDetailsModal = false"
    />

    <!-- Modal de estadísticas detalladas -->
    <AuditStatsModal
      v-if="showStatsModal"
      :stats="stats"
      @close="showStatsModal = false"
    />

    <!-- Modal de confirmación de exportación -->
    <ConfirmModal
      v-if="showExportConfirm"
      title="Confirmar Exportación"
      :message="exportConfirmMessage"
      confirm-text="Exportar"
      confirm-button-class="btn-primary"
      @confirm="confirmExport"
      @cancel="showExportConfirm = false"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import AdminSidebar from '@/components/layout/Common/Sidebar.vue';
import StatsCard from '@/components/reportes/StatsCard.vue';
import AuditTable from '@/components/audit/AuditTable.vue';
import AuditTimeline from '@/components/audit/AuditTimeline.vue';
import AuditCard from '@/components/audit/AuditCard.vue';
import Pagination from '@/components/common/Pagination.vue';
import AuditDetailsModal from '@/components/audit/AuditDetailsModal.vue';
import AuditStatsModal from '@/components/audit/AuditStatsModal.vue';
import ConfirmModal from '@/components/common/ConfirmModal.vue';
import { useAuditStore } from '@/stores/audit';
import { useAuthStore } from '@/stores/auth';
import Swal from 'sweetalert2';

export default {
  name: 'AuditoriaView',
  components: {
    AdminSidebar,
    StatsCard,
    AuditTable,
    AuditTimeline,
    AuditCard,
    Pagination,
    AuditDetailsModal,
    AuditStatsModal,
    ConfirmModal
  },
  setup() {
    const router = useRouter();
    const auditStore = useAuditStore();
    const authStore = useAuthStore();

    // Estado reactivo
    const loading = ref(false);
    const showFilters = ref(false);
    const showDetailsModal = ref(false);
    const showStatsModal = ref(false);
    const showExportConfirm = ref(false);
    const viewMode = ref('table');
    const selectedPeriod = ref('week');
    const realTimeEnabled = ref(false);
    const selectedItem = ref(null);
    const selectedAuditType = ref('activity');
    const exportConfirmMessage = ref('');
    const realTimeInterval = ref(null);

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

    const navbarTitle = ref('Auditoría del Sistema');
    const navbarSubtitle = ref('Monitorea la actividad y seguridad del sistema');
    const searchPlaceholder = ref('Buscar en auditoría...');
    const refreshButtonText = ref('Actualizar');

    // Filtros
    const filters = ref({
      auditType: 'activity',
      usuario: '',
      accion: '',
      modelo: '',
      ip_address: '',
      success: '',
      fecha_desde: '',
      fecha_hasta: ''
    });

    // Estadísticas
    const stats = computed(() => auditStore.stats);

    // Datos filtrados
    const filteredData = computed(() => {
      if (filters.value.auditType === 'activity') {
        return auditStore.activityLogs;
      } else if (filters.value.auditType === 'login') {
        return auditStore.loginHistory;
      } else {
        // Combinar ambos tipos
        return [...auditStore.activityLogs, ...auditStore.loginHistory]
          .sort((a, b) => new Date(b.timestamp || b.login_time) - new Date(a.timestamp || a.login_time));
      }
    });

    // Paginación
    const pagination = computed(() => auditStore.pagination);

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
      loadAuditData();
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

    const handlePeriodChange = (period) => {
      selectedPeriod.value = period;
      loadAuditData();
    };

    const loadInitialData = async () => {
      try {
        loading.value = true;
        await Promise.all([
          auditStore.fetchStats(),
          loadAuditData()
        ]);
      } catch (error) {
        console.error('Error loading initial data:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron cargar los datos de auditoría'
        });
      } finally {
        loading.value = false;
      }
    };

    const loadAuditData = async () => {
      try {
        if (filters.value.auditType === 'activity') {
          await auditStore.fetchActivityLogs(filters.value);
        } else if (filters.value.auditType === 'login') {
          await auditStore.fetchLoginHistory(filters.value);
        } else {
          await Promise.all([
            auditStore.fetchActivityLogs(filters.value),
            auditStore.fetchLoginHistory(filters.value)
          ]);
        }
      } catch (error) {
        console.error('Error loading audit data:', error);
        throw error;
      }
    };

    const handleAuditTypeChange = async () => {
      await loadAuditData();
    };

    const handlePeriodChange = async () => {
      const now = new Date();
      let fecha_desde = '';
      let fecha_hasta = now.toISOString().split('T')[0];

      switch (selectedPeriod.value) {
        case 'today':
          fecha_desde = fecha_hasta;
          break;
        case 'week':
          fecha_desde = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
          break;
        case 'month':
          fecha_desde = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
          break;
        case 'quarter':
          fecha_desde = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
          break;
        case 'year':
          fecha_desde = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
          break;
        case 'custom':
          // No cambiar fechas, usar las que ya están en los filtros
          return;
      }

      filters.value.fecha_desde = fecha_desde;
      filters.value.fecha_hasta = fecha_hasta;
      await applyFilters();
    };

    const applyFilters = async () => {
      try {
        loading.value = true;
        await loadAuditData();
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
        auditType: 'activity',
        usuario: '',
        accion: '',
        modelo: '',
        ip_address: '',
        success: '',
        fecha_desde: '',
        fecha_hasta: ''
      };
      selectedPeriod.value = 'week';
      applyFilters();
    };

    const handleViewDetails = (item, auditType) => {
      selectedItem.value = item;
      selectedAuditType.value = auditType;
      showDetailsModal.value = true;
    };

    const handleSort = async ({ key, order }) => {
      try {
        await auditStore.fetchActivityLogs({
          ...filters.value,
          sort_by: key,
          sort_order: order
        });
      } catch (error) {
        console.error('Error sorting data:', error);
      }
    };

    const handlePageChange = async (page) => {
      try {
        if (filters.value.auditType === 'activity') {
          await auditStore.fetchActivityLogs({ ...filters.value, page });
        } else if (filters.value.auditType === 'login') {
          await auditStore.fetchLoginHistory({ ...filters.value, page });
        }
      } catch (error) {
        console.error('Error changing page:', error);
      }
    };

    const refreshData = async () => {
      await loadInitialData();
    };

    const toggleRealTime = () => {
      realTimeEnabled.value = !realTimeEnabled.value;
      
      if (realTimeEnabled.value) {
        // Iniciar actualización en tiempo real cada 30 segundos
        realTimeInterval.value = setInterval(async () => {
          try {
            await auditStore.fetchStats();
            await loadAuditData();
          } catch (error) {
            console.error('Error in real-time update:', error);
          }
        }, 30000);
      } else {
        // Detener actualización en tiempo real
        if (realTimeInterval.value) {
          clearInterval(realTimeInterval.value);
          realTimeInterval.value = null;
        }
      }
    };

    const exportAuditData = () => {
      exportConfirmMessage.value = '¿Estás seguro de que quieres exportar todos los datos de auditoría?';
      showExportConfirm.value = true;
    };

    const exportFiltered = () => {
      exportConfirmMessage.value = `¿Estás seguro de que quieres exportar los datos filtrados? (${filteredData.value.length} registros)`;
      showExportConfirm.value = true;
    };

    const confirmExport = async () => {
      try {
        await auditStore.exportAuditData({
          ...filters.value,
          format: 'excel'
        });
        Swal.fire({
          icon: 'success',
          title: 'Exportación Iniciada',
          text: 'El archivo se está generando'
        });
      } catch (error) {
        console.error('Error exporting audit data:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo exportar los datos de auditoría'
        });
      } finally {
        showExportConfirm.value = false;
      }
    };

    // Watchers
    watch(() => filters.value.fecha_desde, () => {
      if (filters.value.fecha_desde && filters.value.fecha_hasta) {
        if (new Date(filters.value.fecha_desde) > new Date(filters.value.fecha_hasta)) {
          Swal.fire({
            icon: 'warning',
            title: 'Fechas Inválidas',
            text: 'La fecha desde debe ser anterior a la fecha hasta'
          });
        }
      }
    });

    // Lifecycle
    onMounted(() => {
      loadInitialData();
      checkScreenSize();
      window.addEventListener('resize', checkScreenSize);
    });

    onUnmounted(() => {
      if (realTimeInterval.value) {
        clearInterval(realTimeInterval.value);
      }
      window.removeEventListener('resize', checkScreenSize);
    });

    const checkScreenSize = () => {
      if (window.innerWidth <= 768) {
        sidebarCollapsed.value = true;
        localStorage.setItem('sidebarCollapsed', 'true');
      }
    };

    return {
      // Estado
      loading,
      showFilters,
      showDetailsModal,
      showStatsModal,
      showExportConfirm,
      viewMode,
      selectedPeriod,
      realTimeEnabled,
      selectedItem,
      selectedAuditType,
      exportConfirmMessage,

      // Props para componentes
      brandName,
      userName,
      userRole,
      navbarTitle,
      navbarSubtitle,
      searchPlaceholder,
      refreshButtonText,

      // Datos
      filters,
      stats,
      filteredData,
      pagination,

      // Métodos
      handleMenuClick,
      handleLogout,
      handleSearch,
      handleRefresh,
      handleAuditTypeChange,
      handlePeriodChange,
      applyFilters,
      clearFilters,
      handleViewDetails,
      handleSort,
      handlePageChange,
      refreshData,
      toggleRealTime,
      exportAuditData,
      exportFiltered,
      confirmExport
    };
  }
};
</script>

<style scoped>
/* Estilos específicos para la vista de auditoría */
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
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
  border-color: #2563eb;
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

/* Indicador de tiempo real */
.btn-success {
  position: relative;
}

.btn-success::after {
  content: '';
  position: absolute;
  top: -2px;
  right: -2px;
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }
  
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
  }
  
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
  }
}
</style>

<template>
  <BaseModal
    :show="true"
    :title="`Actividad de ${user.username}`"
    subtitle="Historial de actividades del usuario"
    max-width="5xl"
    @close="closeModal"
  >
    <template #header>
      <div class="flex items-center">
        <div class="bg-blue-100 p-2 rounded-lg mr-3">
          <i class="fas fa-history text-blue-600"></i>
        </div>
        <div>
          <h3 class="text-xl font-bold text-gray-900">Actividad de {{ user.username }}</h3>
          <p class="text-sm text-gray-600 mt-1">Historial de actividades del usuario</p>
        </div>
      </div>
    </template>

    <div class="modal-body-content">
        <!-- Filtros -->
        <div class="filters-section">
          <div class="filters-row">
            <div class="filter-group">
              <label for="activity-filter-action">Acción</label>
              <select id="activity-filter-action" v-model="filters.action" @change="loadActivities">
                <option value="">Todas las acciones</option>
                <option value="login">Login</option>
                <option value="logout">Logout</option>
                <option value="create">Crear</option>
                <option value="update">Actualizar</option>
                <option value="delete">Eliminar</option>
                <option value="view">Ver</option>
                <option value="analysis">Análisis</option>
                <option value="training">Entrenamiento</option>
                <option value="report">Reporte</option>
              </select>
            </div>
            
            <div class="filter-group">
              <label for="activity-filter-model">Modelo</label>
              <select id="activity-filter-model" v-model="filters.model" @change="loadActivities">
                <option value="">Todos los modelos</option>
                <option value="User">Usuario</option>
                <option value="Finca">Finca</option>
                <option value="Lote">Lote</option>
                <option value="CacaoImage">Imagen</option>
                <option value="CacaoPrediction">Predicción</option>
                <option value="TrainingJob">Trabajo de Entrenamiento</option>
                <option value="ReporteGenerado">Reporte</option>
              </select>
            </div>
            
            <div class="filter-group">
              <label for="activity-filter-period">Período</label>
              <select id="activity-filter-period" v-model="filters.period" @change="loadActivities">
                <option value="7">Últimos 7 días</option>
                <option value="30">Últimos 30 días</option>
                <option value="90">Últimos 90 días</option>
                <option value="365">Último año</option>
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

        <!-- Estadísticas -->
        <div class="stats-section">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-number">{{ totalActivities }}</div>
              <div class="stat-label">Total Actividades</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ activitiesToday }}</div>
              <div class="stat-label">Hoy</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ mostCommonAction }}</div>
              <div class="stat-label">Acción Más Común</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ lastActivity }}</div>
              <div class="stat-label">Última Actividad</div>
            </div>
          </div>
        </div>

        <!-- Lista de Actividades -->
        <div class="activities-section">
          <div class="section-header">
            <h4>Historial de Actividades</h4>
            <div class="section-actions">
              <button 
                class="btn btn-sm btn-outline-primary"
                @click="exportActivities"
                :disabled="loading"
              >
                <i class="fas fa-download"></i>
                Exportar
              </button>
            </div>
          </div>

          <div v-if="loading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Cargando actividades...</p>
          </div>

          <div v-else-if="activities.length === 0" class="empty-state">
            <i class="fas fa-history"></i>
            <h3>No hay actividades</h3>
            <p>No se encontraron actividades para este usuario con los filtros aplicados.</p>
          </div>

          <div v-else class="activities-list">
            <div 
              v-for="activity in activities" 
              :key="activity.id"
              class="activity-item"
            >
              <div class="activity-icon">
                <i :class="getActivityIcon(activity.accion)"></i>
              </div>
              
              <div class="activity-content">
                <div class="activity-header">
                  <span class="activity-action" :class="getActionClass(activity.accion)">
                    {{ activity.accion_display }}
                  </span>
                  <span class="activity-model">{{ activity.modelo }}</span>
                  <span class="activity-time">{{ formatDateTime(activity.timestamp) }}</span>
                </div>
                
                <div class="activity-description">
                  {{ activity.descripcion }}
                </div>
                
                <div class="activity-meta">
                  <span v-if="activity.ip_address" class="meta-item">
                    <i class="fas fa-globe"></i>
                    {{ activity.ip_address }}
                  </span>
                  <span v-if="activity.user_agent" class="meta-item">
                    <i class="fas fa-desktop"></i>
                    {{ getBrowserInfo(activity.user_agent) }}
                  </span>
                  <span v-if="activity.objeto_id" class="meta-item">
                    <i class="fas fa-hashtag"></i>
                    ID: {{ activity.objeto_id }}
                  </span>
                </div>
                
                <div v-if="activity.datos_antes || activity.datos_despues" class="activity-data">
                  <div v-if="activity.datos_antes" class="data-section">
                    <h5>Datos Antes</h5>
                    <pre>{{ JSON.stringify(activity.datos_antes, null, 2) }}</pre>
                  </div>
                  <div v-if="activity.datos_despues" class="data-section">
                    <h5>Datos Después</h5>
                    <pre>{{ JSON.stringify(activity.datos_despues, null, 2) }}</pre>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Paginación -->
          <div v-if="pagination.totalPages > 1" class="pagination-container">
            <nav aria-label="Paginación de actividades">
              <ul class="pagination">
                <li class="page-item" :class="{ disabled: pagination.currentPage === 1 }">
                  <button 
                    class="page-link"
                    @click="changePage(pagination.currentPage - 1)"
                    :disabled="pagination.currentPage === 1"
                  >
                    <i class="fas fa-chevron-left"></i>
                  </button>
                </li>
                
                <li 
                  v-for="page in visiblePages" 
                  :key="page"
                  class="page-item"
                  :class="{ active: page === pagination.currentPage }"
                >
                  <button 
                    class="page-link"
                    @click="changePage(page)"
                  >
                    {{ page }}
                  </button>
                </li>
                
                <li class="page-item" :class="{ disabled: pagination.currentPage === pagination.totalPages }">
                  <button 
                    class="page-link"
                    @click="changePage(pagination.currentPage + 1)"
                    :disabled="pagination.currentPage === pagination.totalPages"
                  >
                    <i class="fas fa-chevron-right"></i>
                  </button>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>

    <template #footer>
      <div class="flex justify-end">
        <button 
          type="button" 
          class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          @click="closeModal"
        >
          Cerrar
        </button>
      </div>
    </template>
  </BaseModal>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import BaseModal from '@/components/common/BaseModal.vue'
import { usePagination } from '@/composables/usePagination'

export default {
  name: 'UserActivityModal',
  components: {
    BaseModal
  },
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const adminStore = useAdminStore()

    const loading = ref(false)
    const activities = ref([])
    const totalActivities = ref(0)
    const pageSize = ref(20)

    // Use pagination composable
    const pagination = usePagination({
      initialPage: 1,
      initialItemsPerPage: pageSize.value
    })

    const filters = reactive({
      action: '',
      model: '',
      period: '30'
    })

    // Computed
    const activitiesToday = computed(() => {
      const today = new Date().toDateString()
      return activities.value.filter(activity => 
        new Date(activity.timestamp).toDateString() === today
      ).length
    })

    const mostCommonAction = computed(() => {
      if (activities.value.length === 0) return 'N/A'
      
      const actionCounts = {}
      for (const activity of activities.value) {
        actionCounts[activity.accion] = (actionCounts[activity.accion] || 0) + 1
      }
      
      const mostCommon = Object.entries(actionCounts)
        .sort(([,a], [,b]) => b - a)[0]
      
      return mostCommon ? mostCommon[0] : 'N/A'
    })

    const lastActivity = computed(() => {
      if (activities.value.length === 0) return 'N/A'
      
      const last = activities.value[0]
      const now = new Date()
      const activityTime = new Date(last.timestamp)
      const diffHours = Math.floor((now - activityTime) / (1000 * 60 * 60))
      
      if (diffHours < 1) return 'Hace menos de 1 hora'
      if (diffHours < 24) return `Hace ${diffHours} horas`
      
      const diffDays = Math.floor(diffHours / 24)
      return `Hace ${diffDays} días`
    })

    // Use pagination visiblePages from composable
    const visiblePages = computed(() => pagination.visiblePages.value)

    // Methods
    const loadActivities = async () => {
      loading.value = true
      try {
        const params = {
          user_id: props.user.id,
          page: pagination.currentPage.value,
          page_size: pagination.itemsPerPage.value,
          action: filters.action,
          model: filters.model,
          start_date: getStartDate()
        }
        
        const response = await adminStore.getActivityLogs(params)
        activities.value = response.data.results
        totalActivities.value = response.data.count
        
        // Update pagination from API response
        pagination.updateFromApiResponse({
          page: response.data.page || pagination.currentPage.value,
          page_size: response.data.page_size || pagination.itemsPerPage.value,
          count: response.data.count || 0,
          total_pages: response.data.total_pages || Math.ceil(response.data.count / pagination.itemsPerPage.value)
        })
        
      } catch (error) {
        } finally {
        loading.value = false
      }
    }

    const getStartDate = () => {
      const days = Number.parseInt(filters.period)
      const date = new Date()
      date.setDate(date.getDate() - days)
      return date.toISOString().split('T')[0]
    }

    const clearFilters = () => {
      filters.action = ''
      filters.model = ''
      filters.period = '30'
      pagination.goToPage(1)
      loadActivities()
    }

    const changePage = (page) => {
      if (pagination.goToPage(page)) {
        loadActivities()
      }
    }

    const exportActivities = async () => {
      try {
        const params = {
          user_id: props.user.id,
          action: filters.action,
          model: filters.model,
          start_date: getStartDate(),
          format: 'excel'
        }
        
        const response = await adminStore.exportData('user-activities', 'excel', params)
        
        // Create download link
        const blob = new Blob([response.data], { 
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
        })
        const url = globalThis.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `actividad_${props.user.username}_${new Date().toISOString().split('T')[0]}.xlsx`
        document.body.appendChild(link)
        link.click()
        link.remove()
        globalThis.URL.revokeObjectURL(url)
        
      } catch (error) {
        }
    }

    const closeModal = () => {
      emit('close')
    }

    const formatDateTime = (date) => {
      return new Date(date).toLocaleString('es-ES')
    }

    const getActivityIcon = (action) => {
      const icons = {
        'login': 'fas fa-sign-in-alt',
        'logout': 'fas fa-sign-out-alt',
        'create': 'fas fa-plus',
        'update': 'fas fa-edit',
        'delete': 'fas fa-trash',
        'view': 'fas fa-eye',
        'analysis': 'fas fa-microscope',
        'training': 'fas fa-brain',
        'report': 'fas fa-file-alt',
        'download': 'fas fa-download',
        'upload': 'fas fa-upload',
        'error': 'fas fa-exclamation-triangle'
      }
      return icons[action] || 'fas fa-circle'
    }

    const getActionClass = (action) => {
      const classes = {
        'login': 'action-success',
        'logout': 'action-info',
        'create': 'action-success',
        'update': 'action-warning',
        'delete': 'action-danger',
        'view': 'action-info',
        'analysis': 'action-primary',
        'training': 'action-primary',
        'report': 'action-info',
        'error': 'action-danger'
      }
      return classes[action] || 'action-secondary'
    }

    const getBrowserInfo = (userAgent) => {
      if (!userAgent) return 'N/A'
      
      // Simple browser detection
      if (userAgent.includes('Chrome')) return 'Chrome'
      if (userAgent.includes('Firefox')) return 'Firefox'
      if (userAgent.includes('Safari')) return 'Safari'
      if (userAgent.includes('Edge')) return 'Edge'
      return 'Otro'
    }

    // Lifecycle
    onMounted(() => {
      loadActivities()
    })

    return {
      loading,
      activities,
      totalActivities,
      pagination,
      filters,
      activitiesToday,
      mostCommonAction,
      lastActivity,
      visiblePages,
      loadActivities,
      getStartDate,
      clearFilters,
      changePage,
      exportActivities,
      closeModal,
      formatDateTime,
      getActivityIcon,
      getActionClass,
      getBrowserInfo
    }
  }
}
</script>

<style scoped>
.modal-body-content {
  padding: 0;
}

.filters-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.filters-row {
  display: flex;
  gap: 15px;
  align-items: end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.9rem;
}

.filter-group select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  min-width: 150px;
}

.stats-section {
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.stat-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  border: 1px solid #ecf0f1;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.activities-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 40px;
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

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #ecf0f1;
  display: flex;
  gap: 15px;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon i {
  font-size: 1rem;
  color: #3498db;
}

.activity-content {
  flex: 1;
}

.activity-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.activity-action {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.action-success {
  background-color: #d4edda;
  color: #155724;
}

.action-warning {
  background-color: #fff3cd;
  color: #856404;
}

.action-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.action-info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.action-primary {
  background-color: #cce5ff;
  color: #004085;
}

.action-secondary {
  background-color: #e2e3e5;
  color: #383d41;
}

.activity-model {
  font-weight: 500;
  color: #2c3e50;
}

.activity-time {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.activity-description {
  color: #2c3e50;
  margin-bottom: 10px;
  line-height: 1.4;
}

.activity-meta {
  display: flex;
  gap: 15px;
  font-size: 0.8rem;
  color: #7f8c8d;
  margin-bottom: 10px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.activity-data {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 10px;
  margin-top: 10px;
}

.data-section {
  margin-bottom: 10px;
}

.data-section:last-child {
  margin-bottom: 0;
}

.data-section h5 {
  margin: 0 0 5px 0;
  font-size: 0.9rem;
  color: #2c3e50;
}

.data-section pre {
  margin: 0;
  font-size: 0.8rem;
  color: #495057;
  background: white;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  overflow-x: auto;
}

.pagination-container {
  margin-top: 20px;
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
  color: #1f4e79;
  background-color: #e9ecef;
  border-color: #dee2e6;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #566366;
  color: #ffffff;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #4a5457;
}

.btn-outline-secondary {
  background-color: transparent;
  color: #6c757d;
  border: 1px solid #6c757d;
}

.btn-outline-secondary:hover:not(:disabled) {
  background-color: #6c757d;
  color: white;
}

.btn-outline-primary {
  background-color: transparent;
  color: #3498db;
  border: 1px solid #3498db;
}

.btn-outline-primary:hover:not(:disabled) {
  background-color: #1f4e79;
  color: #ffffff;
}

@media (max-width: 768px) {
  .modal-container {
    width: 98%;
    margin: 5px;
  }
  
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group select {
    min-width: auto;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .activity-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .activity-meta {
    flex-direction: column;
    gap: 5px;
  }
}
</style>

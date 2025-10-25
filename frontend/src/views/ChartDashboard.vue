<template>
  <div class="chart-dashboard">
    <!-- Header del Dashboard -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="header-title">
          <h1>
            <i class="fas fa-chart-line"></i>
            Dashboard de Estadísticas
          </h1>
          <p>Análisis completo del sistema CacaoScan</p>
        </div>
        <div class="header-actions">
          <div class="period-selector">
            <label>Período:</label>
            <select v-model="selectedPeriod" @change="updatePeriod">
              <option value="7">Últimos 7 días</option>
              <option value="30">Últimos 30 días</option>
              <option value="90">Últimos 90 días</option>
              <option value="365">Último año</option>
            </select>
          </div>
          <button 
            class="refresh-btn"
            @click="refreshData"
            :disabled="loading"
          >
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            Actualizar
          </button>
        </div>
      </div>
    </div>

    <!-- Estadísticas Principales -->
    <StatsGrid 
      :stats="mainStats"
      :columns="4"
      @stat-click="handleStatClick"
    />

    <!-- Gráficos Principales -->
    <div class="charts-grid">
      <!-- Gráfico de Actividad -->
      <DashboardWidget
        title="Actividad de Usuarios"
        icon="fas fa-users"
        variant="primary"
        size="large"
        :loading="loading"
        :refreshable="true"
        @refresh="refreshActivityData"
      >
        <template #actions>
          <select v-model="activityChartType" @change="updateActivityChart">
            <option value="line">Línea</option>
            <option value="bar">Barras</option>
          </select>
        </template>
        
        <AdvancedChart
          :chart-data="activityChartData"
          :type="activityChartType"
          :options="activityChartOptions"
          @chart-click="handleActivityClick"
        />
      </DashboardWidget>

      <!-- Gráfico de Calidad -->
      <DashboardWidget
        title="Distribución de Calidad"
        icon="fas fa-star"
        variant="success"
        size="medium"
        :loading="loading"
        @refresh="refreshQualityData"
      >
        <AdvancedChart
          :chart-data="qualityChartData"
          type="doughnut"
          :options="qualityChartOptions"
          @chart-click="handleQualityClick"
        />
      </DashboardWidget>

      <!-- Gráfico de Análisis por Región -->
      <DashboardWidget
        title="Análisis por Región"
        icon="fas fa-map-marker-alt"
        variant="info"
        size="medium"
        :loading="loading"
        @refresh="refreshRegionData"
      >
        <AdvancedChart
          :chart-data="regionChartData"
          type="bar"
          :options="regionChartOptions"
          @chart-click="handleRegionClick"
        />
      </DashboardWidget>

      <!-- Gráfico de Tendencias -->
      <DashboardWidget
        title="Tendencias de Calidad"
        icon="fas fa-trending-up"
        variant="warning"
        size="large"
        :loading="loading"
        @refresh="refreshTrendsData"
      >
        <template #actions>
          <select v-model="trendsMetric" @change="updateTrendsChart">
            <option value="quality">Calidad</option>
            <option value="volume">Volumen</option>
            <option value="defects">Defectos</option>
          </select>
        </template>
        
        <AdvancedChart
          :chart-data="trendsChartData"
          type="line"
          :options="trendsChartOptions"
          @chart-click="handleTrendsClick"
        />
      </DashboardWidget>
    </div>

    <!-- Tablas de Datos -->
    <div class="tables-grid">
      <!-- Tabla de Usuarios Activos -->
      <DashboardWidget
        title="Usuarios Más Activos"
        icon="fas fa-user-check"
        variant="default"
        size="medium"
        :loading="loading"
        footer
      >
        <template #footer>
          <router-link to="/admin/users" class="view-all-link">
            Ver todos los usuarios
          </router-link>
        </template>
        
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Análisis</th>
                <th>Última Actividad</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in activeUsers" :key="user.id">
                <td>
                  <div class="user-cell">
                    <div class="user-avatar">
                      <i class="fas fa-user"></i>
                    </div>
                    <div class="user-info">
                      <strong>{{ user.name }}</strong>
                      <small>{{ user.email }}</small>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="analysis-count">{{ user.analysis_count }}</span>
                </td>
                <td>
                  <span class="last-activity">{{ formatDate(user.last_activity) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </DashboardWidget>

      <!-- Tabla de Fincas Top -->
      <DashboardWidget
        title="Fincas con Mejor Calidad"
        icon="fas fa-seedling"
        variant="success"
        size="medium"
        :loading="loading"
        footer
      >
        <template #footer>
          <router-link to="/admin/fincas" class="view-all-link">
            Ver todas las fincas
          </router-link>
        </template>
        
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Finca</th>
                <th>Calidad Promedio</th>
                <th>Análisis</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="finca in topFincas" :key="finca.id">
                <td>
                  <div class="finca-cell">
                    <strong>{{ finca.name }}</strong>
                    <small>{{ finca.location }}</small>
                  </div>
                </td>
                <td>
                  <div class="quality-cell">
                    <span class="quality-score" :class="getQualityClass(finca.avg_quality)">
                      {{ finca.avg_quality }}%
                    </span>
                    <div class="quality-bar">
                      <div 
                        class="quality-fill" 
                        :style="{ width: finca.avg_quality + '%' }"
                        :class="getQualityClass(finca.avg_quality)"
                      ></div>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="analysis-count">{{ finca.analysis_count }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </DashboardWidget>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>Cargando datos del dashboard...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AdvancedChart from '@/components/charts/AdvancedChart.vue'
import StatsGrid from '@/components/charts/StatsGrid.vue'
import DashboardWidget from '@/components/charts/DashboardWidget.vue'
import { useAuthStore } from '@/stores/auth'
import { useAdminStore } from '@/stores/admin'

export default {
  name: 'ChartDashboard',
  components: {
    AdvancedChart,
    StatsGrid,
    DashboardWidget
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const adminStore = useAdminStore()

    // Estado reactivo
    const loading = ref(false)
    const selectedPeriod = ref('30')
    const activityChartType = ref('line')
    const trendsMetric = ref('quality')

    // Datos de estadísticas
    const stats = ref({})
    const activeUsers = ref([])
    const topFincas = ref([])

    // Datos de gráficos
    const activityData = ref({ labels: [], datasets: [] })
    const qualityData = ref({ labels: [], datasets: [] })
    const regionData = ref({ labels: [], datasets: [] })
    const trendsData = ref({ labels: [], datasets: [] })

    // Estadísticas principales computadas
    const mainStats = computed(() => [
      {
        value: stats.value.total_users || 0,
        label: 'Usuarios Totales',
        icon: 'fas fa-users',
        change: stats.value.users_change || 0,
        changePeriod: 'vs mes anterior',
        variant: 'primary',
        trend: {
          data: stats.value.users_trend || [],
          color: '#3b82f6'
        }
      },
      {
        value: stats.value.total_analyses || 0,
        label: 'Análisis Realizados',
        icon: 'fas fa-chart-line',
        change: stats.value.analyses_change || 0,
        changePeriod: 'vs mes anterior',
        variant: 'success',
        trend: {
          data: stats.value.analyses_trend || [],
          color: '#10b981'
        }
      },
      {
        value: stats.value.avg_quality || 0,
        label: 'Calidad Promedio',
        icon: 'fas fa-star',
        suffix: '%',
        change: stats.value.quality_change || 0,
        changePeriod: 'vs mes anterior',
        variant: 'warning',
        trend: {
          data: stats.value.quality_trend || [],
          color: '#f59e0b'
        }
      },
      {
        value: stats.value.total_fincas || 0,
        label: 'Fincas Registradas',
        icon: 'fas fa-seedling',
        change: stats.value.fincas_change || 0,
        changePeriod: 'vs mes anterior',
        variant: 'info',
        trend: {
          data: stats.value.fincas_trend || [],
          color: '#06b6d4'
        }
      }
    ])

    // Configuración de gráficos
    const activityChartData = computed(() => activityData.value)
    const qualityChartData = computed(() => qualityData.value)
    const regionChartData = computed(() => regionData.value)
    const trendsChartData = computed(() => trendsData.value)

    const activityChartOptions = computed(() => ({
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => value.toLocaleString()
          }
        }
      }
    }))

    const qualityChartOptions = computed(() => ({
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }))

    const regionChartOptions = computed(() => ({
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }))

    const trendsChartOptions = computed(() => ({
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }))

    // Métodos
    const loadDashboardData = async () => {
      loading.value = true
      try {
        await Promise.all([
          loadStats(),
          loadActivityData(),
          loadQualityData(),
          loadRegionData(),
          loadTrendsData(),
          loadActiveUsers(),
          loadTopFincas()
        ])
      } catch (error) {
        console.error('Error loading dashboard data:', error)
      } finally {
        loading.value = false
      }
    }

    const loadStats = async () => {
      try {
        const response = await adminStore.getGeneralStats()
        stats.value = response.data
      } catch (error) {
        console.error('Error loading stats:', error)
      }
    }

    const loadActivityData = async () => {
      try {
        const response = await adminStore.getActivityData(selectedPeriod.value)
        activityData.value = {
          labels: response.data.labels,
          datasets: [{
            label: 'Actividad',
            data: response.data.values,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true
          }]
        }
      } catch (error) {
        console.error('Error loading activity data:', error)
      }
    }

    const loadQualityData = async () => {
      try {
        const response = await adminStore.getQualityDistribution()
        qualityData.value = {
          labels: ['Excelente', 'Buena', 'Regular', 'Baja'],
          datasets: [{
            data: [
              response.data.excelente || 0,
              response.data.buena || 0,
              response.data.regular || 0,
              response.data.baja || 0
            ],
            backgroundColor: [
              '#10b981',
              '#3b82f6',
              '#f59e0b',
              '#ef4444'
            ]
          }]
        }
      } catch (error) {
        console.error('Error loading quality data:', error)
      }
    }

    const loadRegionData = async () => {
      try {
        const response = await adminStore.getRegionStats()
        regionData.value = {
          labels: response.data.labels,
          datasets: [{
            label: 'Análisis por Región',
            data: response.data.values,
            backgroundColor: '#06b6d4'
          }]
        }
      } catch (error) {
        console.error('Error loading region data:', error)
      }
    }

    const loadTrendsData = async () => {
      try {
        const response = await adminStore.getTrendsData(selectedPeriod.value, trendsMetric.value)
        trendsData.value = {
          labels: response.data.labels,
          datasets: [{
            label: trendsMetric.value.charAt(0).toUpperCase() + trendsMetric.value.slice(1),
            data: response.data.values,
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            fill: true
          }]
        }
      } catch (error) {
        console.error('Error loading trends data:', error)
      }
    }

    const loadActiveUsers = async () => {
      try {
        const response = await adminStore.getActiveUsers()
        activeUsers.value = response.data
      } catch (error) {
        console.error('Error loading active users:', error)
      }
    }

    const loadTopFincas = async () => {
      try {
        const response = await adminStore.getTopFincas()
        topFincas.value = response.data
      } catch (error) {
        console.error('Error loading top fincas:', error)
      }
    }

    const refreshData = () => {
      loadDashboardData()
    }

    const refreshActivityData = () => {
      loadActivityData()
    }

    const refreshQualityData = () => {
      loadQualityData()
    }

    const refreshRegionData = () => {
      loadRegionData()
    }

    const refreshTrendsData = () => {
      loadTrendsData()
    }

    const updatePeriod = () => {
      loadDashboardData()
    }

    const updateActivityChart = () => {
      // El gráfico se actualiza automáticamente con el watcher
    }

    const updateTrendsChart = () => {
      loadTrendsData()
    }

    // Event handlers
    const handleStatClick = (stat) => {
      console.log('Stat clicked:', stat)
      // Implementar navegación según la estadística
    }

    const handleActivityClick = (data) => {
      console.log('Activity chart clicked:', data)
    }

    const handleQualityClick = (data) => {
      console.log('Quality chart clicked:', data)
    }

    const handleRegionClick = (data) => {
      console.log('Region chart clicked:', data)
    }

    const handleTrendsClick = (data) => {
      console.log('Trends chart clicked:', data)
    }

    // Utilidades
    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('es-ES')
    }

    const getQualityClass = (quality) => {
      if (quality >= 90) return 'excellent'
      if (quality >= 70) return 'good'
      if (quality >= 50) return 'regular'
      return 'poor'
    }

    // Watchers
    watch(selectedPeriod, () => {
      loadDashboardData()
    })

    watch(trendsMetric, () => {
      loadTrendsData()
    })

    // Lifecycle
    onMounted(async () => {
      // Verificar permisos
      if (!authStore.user?.is_superuser && !authStore.user?.is_staff) {
        router.push('/unauthorized')
        return
      }

      await loadDashboardData()
    })

    return {
      loading,
      selectedPeriod,
      activityChartType,
      trendsMetric,
      mainStats,
      activityChartData,
      qualityChartData,
      regionChartData,
      trendsChartData,
      activityChartOptions,
      qualityChartOptions,
      regionChartOptions,
      trendsChartOptions,
      activeUsers,
      topFincas,
      refreshData,
      refreshActivityData,
      refreshQualityData,
      refreshRegionData,
      refreshTrendsData,
      updatePeriod,
      updateActivityChart,
      updateTrendsChart,
      handleStatClick,
      handleActivityClick,
      handleQualityClick,
      handleRegionClick,
      handleTrendsClick,
      formatDate,
      getQualityClass
    }
  }
}
</script>

<style scoped>
.chart-dashboard {
  padding: 24px;
  background: #f8fafc;
  min-height: 100vh;
}

.dashboard-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title h1 {
  margin: 0 0 8px 0;
  font-size: 1.875rem;
  font-weight: 700;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h1 i {
  color: #3b82f6;
}

.header-title p {
  margin: 0;
  color: #6b7280;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.period-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.period-selector label {
  font-weight: 500;
  color: #374151;
}

.period-selector select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
}

.refresh-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.refresh-btn:hover {
  background: #2563eb;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.tables-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f9fafb;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
}

.user-info strong {
  display: block;
  color: #1f2937;
  font-size: 0.875rem;
}

.user-info small {
  color: #6b7280;
  font-size: 0.75rem;
}

.analysis-count {
  background: #dbeafe;
  color: #1e40af;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.finca-cell strong {
  display: block;
  color: #1f2937;
  font-size: 0.875rem;
}

.finca-cell small {
  color: #6b7280;
  font-size: 0.75rem;
}

.quality-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.quality-score {
  font-weight: 600;
  font-size: 0.875rem;
}

.quality-score.excellent { color: #10b981; }
.quality-score.good { color: #3b82f6; }
.quality-score.regular { color: #f59e0b; }
.quality-score.poor { color: #ef4444; }

.quality-bar {
  width: 60px;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.quality-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.quality-fill.excellent { background: #10b981; }
.quality-fill.good { background: #3b82f6; }
.quality-fill.regular { background: #f59e0b; }
.quality-fill.poor { background: #ef4444; }

.last-activity {
  color: #6b7280;
  font-size: 0.75rem;
}

.view-all-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
}

.view-all-link:hover {
  text-decoration: underline;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  background: white;
  padding: 32px;
  border-radius: 12px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-content p {
  margin: 0;
  color: #6b7280;
  font-size: 1rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .tables-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .chart-dashboard {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .dashboard-header {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .header-title h1 {
    font-size: 1.5rem;
  }
  
  .period-selector {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

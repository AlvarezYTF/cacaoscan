<template>
  <div class="admin-dashboard">
    <!-- Header del Dashboard -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="header-title">
          <h1 class="dashboard-title">
            <i class="fas fa-tachometer-alt"></i>
            Dashboard de Administración
          </h1>
          <p>Panel de control completo del sistema CacaoScan</p>
        </div>
        <div class="header-actions">
          <div class="period-selector">
            <label>Período:</label>
            <select v-model="selectedPeriod" @change="updatePeriod">
              <option value="7">Últimos 7 días</option>
              <option value="30">Últimos 30 días</option>
              <option value="90">Últimos 90 días</option>
            </select>
          </div>
          <button 
            class="btn btn-primary"
            @click="refreshData"
            :disabled="loading"
          >
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            Actualizar
          </button>
        </div>
      </div>
    </div>

    <!-- Estadísticas Generales con nuevos componentes -->
    <StatsGrid 
      :stats="mainStats"
      :columns="4"
      @stat-click="handleStatClick"
    />

    <!-- Gráficos Principales con nuevos componentes -->
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
    </div>

      <div class="content-row">
        <!-- Tabla de Usuarios Recientes -->
        <div class="table-container">
          <div class="table-header">
            <h3>Usuarios Recientes</h3>
            <router-link to="/admin/users" class="btn btn-sm btn-outline-primary">
              Ver Todos
            </router-link>
          </div>
          <div class="table-body">
            <table class="table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Email</th>
                  <th>Rol</th>
                  <th>Registro</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in recentUsers" :key="user.id">
                  <td>
                    <div class="user-info">
                      <div class="user-avatar">
                        <i class="fas fa-user"></i>
                      </div>
                      <div class="user-details">
                        <strong>{{ user.first_name }} {{ user.last_name }}</strong>
                        <small>@{{ user.username }}</small>
                      </div>
                </div>
                  </td>
                  <td>{{ user.email }}</td>
                  <td>
                    <span class="badge" :class="getRoleBadgeClass(user.role)">
                      {{ user.role }}
                    </span>
                  </td>
                  <td>{{ formatDate(user.date_joined) }}</td>
                  <td>
                    <span class="badge" :class="user.is_active ? 'badge-success' : 'badge-danger'">
                      {{ user.is_active ? 'Activo' : 'Inactivo' }}
                    </span>
                  </td>
                  <td>
                    <div class="action-buttons">
                      <button 
                        class="btn btn-sm btn-outline-primary"
                        @click="viewUser(user.id)"
                      >
                        <i class="fas fa-eye"></i>
                  </button>
                      <button 
                        class="btn btn-sm btn-outline-warning"
                        @click="editUser(user.id)"
                      >
                        <i class="fas fa-edit"></i>
                  </button>
                </div>
                  </td>
                </tr>
              </tbody>
            </table>
              </div>
            </div>
            
        <!-- Tabla de Actividad Reciente -->
        <div class="table-container">
          <div class="table-header">
            <h3>Actividad Reciente</h3>
            <router-link to="/admin/audit" class="btn btn-sm btn-outline-primary">
              Ver Auditoría
            </router-link>
                </div>
          <div class="table-body">
            <table class="table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Acción</th>
                  <th>Modelo</th>
                  <th>Fecha</th>
                  <th>IP</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="activity in recentActivities" :key="activity.id">
                  <td>{{ activity.usuario || 'Anónimo' }}</td>
                  <td>
                    <span class="badge" :class="getActionBadgeClass(activity.accion)">
                      {{ activity.accion_display }}
                    </span>
                  </td>
                  <td>{{ activity.modelo }}</td>
                  <td>{{ formatDateTime(activity.timestamp) }}</td>
                  <td>{{ activity.ip_address || 'N/A' }}</td>
                </tr>
              </tbody>
            </table>
                  </div>
                </div>
              </div>

      <!-- Alertas y Notificaciones -->
      <div class="content-row">
        <div class="alerts-container">
          <div class="alert-header">
            <h3>Alertas del Sistema</h3>
          </div>
          <div class="alert-body">
            <div v-if="alerts.length === 0" class="no-alerts">
              <i class="fas fa-check-circle"></i>
              <p>No hay alertas activas</p>
            </div>
            <div v-else>
              <div 
                v-for="alert in alerts" 
                :key="alert.id"
                class="alert"
                :class="`alert-${alert.type}`"
              >
                <div class="alert-icon">
                  <i :class="getAlertIcon(alert.type)"></i>
          </div>
                <div class="alert-content">
                  <h4>{{ alert.title }}</h4>
                  <p>{{ alert.message }}</p>
                  <small>{{ formatDateTime(alert.created_at) }}</small>
                </div>
                <div class="alert-actions">
                  <button 
                    class="btn btn-sm btn-outline-secondary"
                    @click="dismissAlert(alert.id)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
                        </div>
                      </div>

        <!-- Estadísticas de Reportes -->
        <div class="reports-container">
          <div class="reports-header">
            <h3>Reportes Generados</h3>
            <router-link to="/admin/reports" class="btn btn-sm btn-outline-primary">
              Gestionar Reportes
            </router-link>
          </div>
          <div class="reports-body">
            <div class="reports-stats">
              <div class="report-stat">
                <h4>{{ reportStats.total_reportes || 0 }}</h4>
                <p>Total Reportes</p>
            </div>
              <div class="report-stat">
                <h4>{{ reportStats.reportes_completados || 0 }}</h4>
                <p>Completados</p>
                </div>
              <div class="report-stat">
                <h4>{{ reportStats.reportes_generando || 0 }}</h4>
                <p>Generando</p>
                </div>
              <div class="report-stat">
                <h4>{{ reportStats.reportes_fallidos || 0 }}</h4>
                <p>Fallidos</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Cargando datos...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Chart from 'chart.js/auto'
import Swal from 'sweetalert2'
import { useAuthStore } from '@/stores/auth'
import { useAdminStore } from '@/stores/admin'
import AdvancedChart from '@/components/charts/AdvancedChart.vue'
import StatsGrid from '@/components/charts/StatsGrid.vue'
import DashboardWidget from '@/components/charts/DashboardWidget.vue'

export default {
  name: 'AdminDashboard',
  components: {
    AdvancedChart,
    StatsGrid,
    DashboardWidget
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const adminStore = useAdminStore()

    // Reactive data
    const loading = ref(false)
    const stats = ref({})
    const recentUsers = ref([])
    const recentActivities = ref([])
    const alerts = ref([])
    const reportStats = ref({})
    const selectedPeriod = ref('30')
    const activityChartType = ref('line')

    // Datos de gráficos
    const activityData = ref({ labels: [], datasets: [] })
    const qualityData = ref({ labels: [], datasets: [] })

    // Estadísticas principales computadas
    const mainStats = computed(() => [
      {
        value: stats.value.total_users || 0,
        label: 'Usuarios Totales',
        icon: 'fas fa-users',
        change: stats.value.new_users_today || 0,
        changePeriod: 'hoy',
        variant: 'primary',
        trend: {
          data: stats.value.users_trend || [],
          color: '#3498db'
        }
      },
      {
        value: stats.value.total_fincas || 0,
        label: 'Fincas Registradas',
        icon: 'fas fa-seedling',
        change: stats.value.new_fincas_today || 0,
        changePeriod: 'hoy',
        variant: 'success',
        trend: {
          data: stats.value.fincas_trend || [],
          color: '#2ecc71'
        }
      },
      {
        value: stats.value.total_analyses || 0,
        label: 'Análisis Realizados',
        icon: 'fas fa-chart-line',
        change: stats.value.analyses_today || 0,
        changePeriod: 'hoy',
        variant: 'info',
        trend: {
          data: stats.value.analyses_trend || [],
          color: '#17a2b8'
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
          color: '#f39c12'
        }
      }
    ])

    // Configuración de gráficos
    const activityChartData = computed(() => activityData.value)
    const qualityChartData = computed(() => qualityData.value)

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

    // Methods
    const loadDashboardData = async () => {
      loading.value = true
      try {
        await Promise.all([
          loadStats(),
          loadRecentUsers(),
          loadRecentActivities(),
          loadAlerts(),
          loadReportStats(),
          loadQualityData(),
          updateActivityChart()
        ])
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron cargar los datos del dashboard'
        })
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

    const loadRecentUsers = async () => {
      try {
        const response = await adminStore.getRecentUsers()
        recentUsers.value = response.data
      } catch (error) {
        console.error('Error loading recent users:', error)
      }
    }

    const loadRecentActivities = async () => {
      try {
        const response = await adminStore.getRecentActivities()
        recentActivities.value = response.data
      } catch (error) {
        console.error('Error loading recent activities:', error)
      }
    }

    const loadAlerts = async () => {
      try {
        const response = await adminStore.getSystemAlerts()
        alerts.value = response.data
      } catch (error) {
        console.error('Error loading alerts:', error)
      }
    }

    const loadReportStats = async () => {
      try {
        const response = await adminStore.getReportStats()
        reportStats.value = response.data
      } catch (error) {
        console.error('Error loading report stats:', error)
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
              '#28a745',
              '#17a2b8',
              '#ffc107',
              '#dc3545'
            ]
          }]
        }
      } catch (error) {
        console.error('Error loading quality data:', error)
      }
    }

    const refreshData = () => {
      loadDashboardData()
    }

    const updateActivityChart = async () => {
      try {
        const response = await adminStore.getActivityData(selectedPeriod.value)
        activityData.value = {
          labels: response.data.labels,
          datasets: [{
            label: 'Actividad',
            data: response.data.values,
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            fill: true
          }]
        }
      } catch (error) {
        console.error('Error updating activity chart:', error)
      }
    }

    const refreshActivityData = () => {
      updateActivityChart()
    }

    const refreshQualityData = () => {
      loadQualityData()
    }

    const updatePeriod = () => {
      loadDashboardData()
    }

    const createCharts = () => {
      createActivityChart()
      createQualityChart()
    }

    const createActivityChart = () => {
      if (activityChartInstance) {
        activityChartInstance.destroy()
      }

      const ctx = activityChart.value.getContext('2d')
      activityChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: [],
          datasets: [{
            label: 'Actividad',
            data: [],
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.1
          }]
        },
        options: {
      responsive: true,
          maintainAspectRatio: false,
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
        }
      })
    }

    const createQualityChart = () => {
      if (qualityChartInstance) {
        qualityChartInstance.destroy()
      }

      const ctx = qualityChart.value.getContext('2d')
      qualityChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Excelente', 'Buena', 'Regular', 'Baja'],
          datasets: [{
            data: [0, 0, 0, 0],
            backgroundColor: [
              '#28a745',
              '#17a2b8',
              '#ffc107',
              '#dc3545'
            ]
          }]
        },
        options: {
      responsive: true,
          maintainAspectRatio: false,
      plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })
    }

    const updateActivityChartData = (data) => {
      if (activityChartInstance) {
        activityChartInstance.data.labels = data.labels
        activityChartInstance.data.datasets[0].data = data.values
        activityChartInstance.update()
      }
    }

    const updateQualityChartData = (data) => {
      if (qualityChartInstance) {
        qualityChartInstance.data.datasets[0].data = [
          data.excelente || 0,
          data.buena || 0,
          data.regular || 0,
          data.baja || 0
        ]
        qualityChartInstance.update()
      }
    }

    // Utility methods
    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('es-ES')
    }

    const formatDateTime = (date) => {
      return new Date(date).toLocaleString('es-ES')
    }

    const getRoleBadgeClass = (role) => {
      const classes = {
        'Administrador': 'badge-danger',
        'Agricultor': 'badge-success',
        'Técnico': 'badge-info'
      }
      return classes[role] || 'badge-secondary'
    }

    const getActionBadgeClass = (action) => {
      const classes = {
        'create': 'badge-success',
        'update': 'badge-warning',
        'delete': 'badge-danger',
        'view': 'badge-info',
        'login': 'badge-primary',
        'logout': 'badge-secondary'
      }
      return classes[action] || 'badge-secondary'
    }

    const getQualityChangeClass = (change) => {
      if (change > 0) return 'positive'
      if (change < 0) return 'negative'
      return 'neutral'
    }

    const getQualityChangeIcon = (change) => {
      if (change > 0) return 'fas fa-arrow-up'
      if (change < 0) return 'fas fa-arrow-down'
      return 'fas fa-minus'
    }

    const getAlertIcon = (type) => {
      const icons = {
        'success': 'fas fa-check-circle',
        'warning': 'fas fa-exclamation-triangle',
        'error': 'fas fa-times-circle',
        'info': 'fas fa-info-circle'
      }
      return icons[type] || 'fas fa-info-circle'
    }

    const viewUser = (userId) => {
      router.push(`/admin/users/${userId}`)
    }

    const editUser = (userId) => {
      router.push(`/admin/users/${userId}/edit`)
    }

    const dismissAlert = async (alertId) => {
      try {
        await adminStore.dismissAlert(alertId)
        alerts.value = alerts.value.filter(alert => alert.id !== alertId)
        Swal.fire({
          icon: 'success',
          title: 'Alerta Descartada',
          text: 'La alerta ha sido descartada exitosamente'
        })
      } catch (error) {
        console.error('Error dismissing alert:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo descartar la alerta'
        })
      }
    }

    // Event handlers para gráficos
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

    // Lifecycle
    onMounted(async () => {
      // Verificar permisos de administrador
      if (!authStore.user?.is_superuser && !authStore.user?.is_staff) {
        router.push('/unauthorized')
        return
      }

      await loadDashboardData()
      
      // Crear gráficos después de cargar los datos
      setTimeout(() => {
        createCharts()
        updateActivityChart()
      }, 100)
    })

    onUnmounted(() => {
      if (activityChartInstance) {
        activityChartInstance.destroy()
      }
      if (qualityChartInstance) {
        qualityChartInstance.destroy()
      }
    })

    return {
      loading,
      stats,
      recentUsers,
      recentActivities,
      alerts,
      reportStats,
      selectedPeriod,
      activityChartType,
      mainStats,
      activityChartData,
      qualityChartData,
      activityChartOptions,
      qualityChartOptions,
      refreshData,
      updateActivityChart,
      refreshActivityData,
      refreshQualityData,
      updatePeriod,
      handleStatClick,
      handleActivityClick,
      handleQualityClick,
      formatDate,
      formatDateTime,
      getRoleBadgeClass,
      getActionBadgeClass,
      getQualityChangeClass,
      getQualityChangeIcon,
      getAlertIcon,
      viewUser,
      editUser,
      dismissAlert
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
  background-color: #f8f9fa;
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

.header-title {
  flex: 1;
}

.dashboard-title {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 1.875rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.dashboard-title i {
  color: #3498db;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2.5rem;
  margin-right: 20px;
  color: #3498db;
}

.stat-content h3 {
  margin: 0;
  font-size: 2rem;
  color: #2c3e50;
}

.stat-content p {
  margin: 5px 0;
  color: #7f8c8d;
  font-weight: 500;
}

.stat-change {
  font-size: 0.9rem;
  font-weight: 500;
}

.stat-change.positive {
  color: #27ae60;
}

.stat-change.negative {
  color: #e74c3c;
}

.stat-change.neutral {
  color: #95a5a6;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.content-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-container,
.table-container,
.alerts-container,
.reports-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.chart-header,
.table-header,
.alert-header,
.reports-header {
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header h3,
.table-header h3,
.alert-header h3,
.reports-header h3 {
  margin: 0;
  color: #2c3e50;
}

.chart-body {
  padding: 20px;
  height: 300px;
}

.table-body {
  padding: 0;
}

.table {
  margin: 0;
}

.table th {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  font-weight: 600;
  color: #495057;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.user-details strong {
  display: block;
  color: #2c3e50;
}

.user-details small {
  color: #7f8c8d;
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

.action-buttons {
  display: flex;
  gap: 5px;
}

.alert-body {
  padding: 20px;
}

.no-alerts {
  text-align: center;
  color: #7f8c8d;
  padding: 40px;
}

.no-alerts i {
  font-size: 3rem;
  margin-bottom: 10px;
  color: #27ae60;
}

.alert {
  display: flex;
  align-items: center;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  border-left: 4px solid;
}

.alert-success {
  background-color: #d4edda;
  border-left-color: #28a745;
  color: #155724;
}

.alert-warning {
  background-color: #fff3cd;
  border-left-color: #ffc107;
  color: #856404;
}

.alert-error {
  background-color: #f8d7da;
  border-left-color: #dc3545;
  color: #721c24;
}

.alert-info {
  background-color: #d1ecf1;
  border-left-color: #17a2b8;
  color: #0c5460;
}

.alert-icon {
  font-size: 1.5rem;
  margin-right: 15px;
}

.alert-content {
  flex: 1;
}

.alert-content h4 {
  margin: 0 0 5px 0;
  font-size: 1rem;
}

.alert-content p {
  margin: 0 0 5px 0;
  font-size: 0.9rem;
}

.alert-content small {
  color: #6c757d;
}

.alert-actions {
  margin-left: 15px;
}

.reports-body {
  padding: 20px;
}

.reports-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.report-stat {
  text-align: center;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.report-stat h4 {
  margin: 0 0 5px 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.report-stat p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-spinner {
  background: white;
  padding: 30px;
  border-radius: 10px;
  text-align: center;
}

.loading-spinner i {
  font-size: 2rem;
  color: #3498db;
  margin-bottom: 10px;
}

.loading-spinner p {
  margin: 0;
  color: #2c3e50;
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .period-selector {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .content-row {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .reports-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
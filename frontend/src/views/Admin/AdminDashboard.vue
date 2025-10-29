<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar Component -->
    <AdminSidebar :brand-name="brandName" :user-name="userName" :user-role="userRole" :current-route="$route.path"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick" @logout="handleLogout" @toggle-collapse="toggleSidebarCollapse" />

    <!-- Main Content -->
    <div class="p-6 transition-all duration-300" :class="isSidebarCollapsed ? 'sm:ml-20' : 'sm:ml-64'">
      <!-- Dashboard Header -->
      <div class="mb-8">
        <div
          class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
          <div class="px-6 py-4">
            <div class="flex-1">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">Dashboard de Administración</h1>
            <p class="text-gray-600 text-lg">Panel de control completo del sistema CacaoScan</p>
            </div>
          </div>
          </div>
      </div>
      <!-- KPI Cards Component -->
      <div class="mb-8">
        <KPICards :cards="kpiCards" @card-click="handleKPICardClick" />
      </div>

      <!-- Charts Component -->
      <div class="mb-8">
        <DashboardCharts :activity-chart-title="activityChartTitle" :quality-chart-title="qualityChartTitle"
          :activity-chart-data="activityChartData" :quality-chart-data="qualityChartData"
          :activity-chart-options="activityChartOptions" :quality-chart-options="qualityChartOptions" :loading="loading"
          :initial-activity-chart-type="activityChartType" @activity-chart-type-change="handleActivityChartTypeChange"
          @activity-refresh="handleActivityRefresh" @quality-refresh="handleQualityRefresh"
          @activity-click="handleActivityClick" @quality-click="handleQualityClick" />
      </div>

      <!-- Tables Component -->
      <div class="mb-8">
        <DashboardTables :users-table-title="usersTableTitle" :users-table-link="usersTableLink"
          :users-table-link-text="usersTableLinkText" :activity-table-title="activityTableTitle"
          :activity-table-link="activityTableLink" :activity-table-link-text="activityTableLinkText"
          :recent-users="recentUsers" :recent-activities="recentActivities" @view-user="handleViewUser"
          @edit-user="handleEditUser" />
      </div>

      <!-- Alerts and Reports Component -->
      <div class="mb-8">
        <DashboardAlerts :alerts-title="alertsTitle" :no-alerts-message="noAlertsMessage" :reports-title="reportsTitle"
          :reports-link="reportsLink" :reports-link-text="reportsLinkText" :total-reports-label="totalReportsLabel"
          :completed-reports-label="completedReportsLabel" :generating-reports-label="generatingReportsLabel"
          :failed-reports-label="failedReportsLabel" :alerts="alerts" :report-stats="reportStats"
          @dismiss-alert="handleDismissAlert" />
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
import { useConfigStore } from '@/stores/config'
import { useAdminStore } from '@/stores/admin'
import AdminSidebar from '@/components/layout/Common/Sidebar.vue'
import KPICards from '@/components/admin/AdminDashboardComponents/KPICards.vue'
import DashboardCharts from '@/components/admin/AdminDashboardComponents/DashboardCharts.vue'
import DashboardTables from '@/components/admin/AdminDashboardComponents/DashboardTables.vue'
import DashboardAlerts from '@/components/admin/AdminDashboardComponents/DashboardAlerts.vue'
import LoadingSpinner from '@/components/admin/AdminGeneralComponents/LoadingSpinner.vue'

export default {
  name: 'AdminDashboard',
  components: {
    AdminSidebar,
    KPICards,
    DashboardCharts,
    DashboardTables,
    DashboardAlerts,
    LoadingSpinner
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const adminStore = useAdminStore()
    const configStore = useConfigStore()

    // Reactive data
    const loading = ref(false)
    const stats = ref({})
    const recentUsers = ref([])
    const recentActivities = ref([])
    const alerts = ref([])
    const reportStats = ref({})
    const selectedPeriod = ref('30')
    const activityChartType = ref('line')

    // Chart refs
    const activityChart = ref(null)
    const qualityChart = ref(null)
    let activityChartInstance = null
    let qualityChartInstance = null

    // Datos de gráficos
    const activityData = ref({ labels: [], datasets: [] })
    const qualityData = ref({ labels: [], datasets: [] })

    // Sidebar properties
    const brandName = computed(() => configStore.brandName)
    const userName = computed(() => {
      const user = authStore.user
      return user ? `${user.first_name} ${user.last_name}`.trim() || user.username : 'Admin User'
    })
    const userRole = computed(() => {
      const role = authStore.userRole || 'Usuario'
      // Normalize role for sidebar - Backend returns: 'admin', 'analyst', or 'farmer'
      if (role === 'admin') return 'admin'
      if (role === 'farmer') return 'agricultor'
      return 'admin' // Default to admin for AdminDashboard
    })

    // Navbar properties
    const navbarTitle = ref('Dashboard de Administración')
    const navbarSubtitle = ref('Panel de control completo del sistema CacaoScan')
    const searchPlaceholder = ref('Buscar usuarios, análisis, reportes...')
    const refreshButtonText = ref('Actualizar')
    const searchQuery = ref('')

    // Sidebar collapse state
    const isSidebarCollapsed = ref(false)

    const toggleSidebarCollapse = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value
      localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value)
    }

    // Charts properties
    const activityChartTitle = ref('Actividad de Usuarios')
    const qualityChartTitle = ref('Distribución de Calidad')

    // Tables properties
    const usersTableTitle = ref('Usuarios Recientes')
    const usersTableLink = ref('/admin/users')
    const usersTableLinkText = ref('Ver Todos')
    const activityTableTitle = ref('Actividad Reciente')
    const activityTableLink = ref('/admin/audit')
    const activityTableLinkText = ref('Ver Auditoría')

    // Alerts properties
    const alertsTitle = ref('Alertas del Sistema')
    const noAlertsMessage = ref('No hay alertas activas')
    const reportsTitle = ref('Reportes Generados')
    const reportsLink = ref('/admin/reports')
    const reportsLinkText = ref('Gestionar Reportes')
    const totalReportsLabel = ref('Total Reportes')
    const completedReportsLabel = ref('Completados')
    const generatingReportsLabel = ref('Generando')
    const failedReportsLabel = ref('Fallidos')

    // KPI Cards data
    const kpiCards = computed(() => [
      {
        id: 'users',
        value: stats.value.total_users || 0,
        label: 'Usuarios Totales',
        iconPath: 'M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z',
        change: stats.value.new_users_today || 0,
        changePeriod: 'hoy',
        variant: 'primary',
        trend: {
          data: stats.value.users_trend || [],
          direction: stats.value.new_users_today > 0 ? 'up' : 'stable'
        }
      },
      {
        id: 'fincas',
        value: stats.value.total_fincas || 0,
        label: 'Fincas Registradas',
        iconPath: 'M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z',
        fillRule: 'evenodd',
        clipRule: 'evenodd',
        change: stats.value.new_fincas_today || 0,
        changePeriod: 'hoy',
        variant: 'success',
        trend: {
          data: stats.value.fincas_trend || [],
          direction: stats.value.new_fincas_today > 0 ? 'up' : 'stable'
        }
      },
      {
        id: 'analyses',
        value: stats.value.total_analyses || 0,
        label: 'Análisis Realizados',
        iconPath: 'M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z',
        fillRule: 'evenodd',
        clipRule: 'evenodd',
        change: stats.value.analyses_today || 0,
        changePeriod: 'hoy',
        variant: 'info',
        trend: {
          data: stats.value.analyses_trend || [],
          direction: stats.value.analyses_today > 0 ? 'up' : 'stable'
        }
      },
      {
        id: 'quality',
        value: stats.value.avg_quality || 0,
        label: 'Calidad Promedio',
        iconPath: 'M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z',
        suffix: '%',
        change: stats.value.quality_change || 0,
        changePeriod: 'vs mes anterior',
        variant: 'warning',
        trend: {
          data: stats.value.quality_trend || [],
          direction: stats.value.quality_change > 0 ? 'up' : stats.value.quality_change < 0 ? 'down' : 'stable'
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
        // Asegurar que sea un array
        recentUsers.value = Array.isArray(response.data) ? response.data : []
        console.log('👥 Recent users loaded:', recentUsers.value.length, 'items')
      } catch (error) {
        console.error('Error loading recent users:', error)
        recentUsers.value = []
      }
    }

    const loadRecentActivities = async () => {
      try {
        const response = await adminStore.getRecentActivities()
        // Asegurar que sea un array
        recentActivities.value = Array.isArray(response.data) ? response.data : []
        console.log('📊 Recent activities loaded:', recentActivities.value.length, 'items')
      } catch (error) {
        console.error('Error loading recent activities:', error)
        recentActivities.value = []
      }
    }

    const loadAlerts = async () => {
      try {
        const response = await adminStore.getSystemAlerts()
        // Asegurar que sea un array
        alerts.value = Array.isArray(response.data) ? response.data : []
        console.log('🚨 Alerts loaded:', alerts.value.length, 'items')
      } catch (error) {
        console.error('Error loading alerts:', error)
        alerts.value = []
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
        'Administrador': 'bg-red-100 text-red-800',
        'Agricultor': 'bg-green-100 text-green-800',
        'Técnico': 'bg-blue-100 text-blue-800'
      }
      return classes[role] || 'bg-gray-100 text-gray-800'
    }

    const getActionBadgeClass = (action) => {
      const classes = {
        'create': 'bg-green-100 text-green-800',
        'update': 'bg-amber-100 text-amber-800',
        'delete': 'bg-red-100 text-red-800',
        'view': 'bg-blue-100 text-blue-800',
        'login': 'bg-indigo-100 text-indigo-800',
        'logout': 'bg-gray-100 text-gray-800'
      }
      return classes[action] || 'bg-gray-100 text-gray-800'
    }

    const getAlertBorderClass = (type) => {
      const classes = {
        'success': 'border-green-400 bg-green-50',
        'warning': 'border-amber-400 bg-amber-50',
        'error': 'border-red-400 bg-red-50',
        'info': 'border-blue-400 bg-blue-50'
      }
      return classes[type] || 'border-gray-400 bg-gray-50'
    }

    const getAlertIconClass = (type) => {
      const classes = {
        'success': 'text-green-500',
        'warning': 'text-amber-500',
        'error': 'text-red-500',
        'info': 'text-blue-500'
      }
      return classes[type] || 'text-gray-500'
    }

    const getAlertIconPath = (type) => {
      const paths = {
        'success': 'M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z',
        'warning': 'M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z',
        'error': 'M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z',
        'info': 'M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z'
      }
      return paths[type] || 'M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z'
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

    // Sidebar event handlers
    const handleMenuClick = (menuItem) => {
      console.log('Menu clicked:', menuItem)
      
      if (menuItem.route) {
        // Navigate to the route
        router.push(menuItem.route)
      }
    }

    const handleLogout = async () => {
      try {
        await authStore.logout()
        // No redirigir aquí - authStore.logout() ya maneja la redirección
      } catch (error) {
        console.error('Error during logout:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo cerrar la sesión'
        })
      }
    }

    // Navbar event handlers
    const handleSearch = (query) => {
      console.log('Search query:', query)
      searchQuery.value = query
      // Implementar lógica de búsqueda aquí
      if (query.trim()) {
        // Filtrar datos según la búsqueda
        console.log('Searching for:', query)
      }
    }

    const handlePeriodChange = (period) => {
      console.log('Period changed to:', period)
      selectedPeriod.value = period
      updatePeriod()
    }

    const handleRefresh = () => {
      console.log('Refreshing data...')
      refreshData()
    }

    // KPI Cards event handler
    const handleKPICardClick = (card) => {
      console.log('KPI Card clicked:', card)
      // Implementar navegación según la tarjeta
      switch (card.id) {
        case 'users':
          router.push('/admin/users')
          break
        case 'fincas':
          router.push('/admin/fincas')
          break
        case 'analyses':
          router.push('/admin/analysis')
          break
        case 'quality':
          router.push('/admin/reports')
          break
        default:
          console.log('Unknown card clicked:', card.id)
      }
    }

    // Charts event handlers
    const handleActivityChartTypeChange = (chartType) => {
      console.log('Activity chart type changed to:', chartType)
      activityChartType.value = chartType
      updateActivityChart()
    }

    const handleActivityRefresh = () => {
      console.log('Refreshing activity data...')
      refreshActivityData()
    }

    const handleQualityRefresh = () => {
      console.log('Refreshing quality data...')
      refreshQualityData()
    }

    const handleActivityClick = (event) => {
      console.log('Activity chart clicked:', event)
    }

    const handleQualityClick = (event) => {
      console.log('Quality chart clicked:', event)
    }

    // Tables event handlers
    const handleViewUser = (userId) => {
      console.log('View user clicked:', userId)
      router.push(`/admin/users/${userId}`)
    }

    const handleEditUser = (userId) => {
      console.log('Edit user clicked:', userId)
      router.push(`/admin/users/${userId}/edit`)
    }

    // Alerts event handlers
    const handleDismissAlert = (alertId) => {
      console.log('Dismiss alert clicked:', alertId)
      // Implementar lógica para descartar alerta
      Swal.fire({
        title: '¿Descartar alerta?',
        text: 'Esta acción no se puede deshacer',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, descartar',
        cancelButtonText: 'Cancelar'
      }).then((result) => {
        if (result.isConfirmed) {
          // Aquí implementarías la lógica para descartar la alerta
          console.log('Alert dismissed:', alertId)
          Swal.fire('Descartada', 'La alerta ha sido descartada', 'success')
        }
      })
    }

    // Event handlers para gráficos
    const handleStatClick = (stat) => {
      console.log('Stat clicked:', stat)
      // Implementar navegación según la estadística
    }

    // Lifecycle
    onMounted(async () => {
      // Verificar permisos de administrador usando el sistema de roles
      if (!authStore.isAdmin) {
        console.warn('🚫 Usuario sin permisos de admin:', {
          userRole: authStore.userRole,
          isAdmin: authStore.isAdmin,
          user: authStore.user
        })
        router.push('/acceso-denegado')
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
      isSidebarCollapsed,
      toggleSidebarCollapse,
      recentActivities,
      alerts,
      reportStats,
      selectedPeriod,
      activityChartType,
      activityChart,
      qualityChart,
      brandName,
      userName,
      userRole,
      navbarTitle,
      navbarSubtitle,
      searchPlaceholder,
      refreshButtonText,
      searchQuery,
      activityChartTitle,
      qualityChartTitle,
      usersTableTitle,
      usersTableLink,
      usersTableLinkText,
      activityTableTitle,
      activityTableLink,
      activityTableLinkText,
      alertsTitle,
      noAlertsMessage,
      reportsTitle,
      reportsLink,
      reportsLinkText,
      totalReportsLabel,
      completedReportsLabel,
      generatingReportsLabel,
      failedReportsLabel,
      kpiCards,
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
      handleMenuClick,
      handleLogout,
      handleSearch,
      handlePeriodChange,
      handleRefresh,
      handleKPICardClick,
      handleActivityChartTypeChange,
      handleActivityRefresh,
      handleQualityRefresh,
      handleActivityClick,
      handleQualityClick,
      handleViewUser,
      handleEditUser,
      handleDismissAlert,
      formatDate,
      formatDateTime,
      getRoleBadgeClass,
      getActionBadgeClass,
      getAlertBorderClass,
      getAlertIconClass,
      getAlertIconPath,
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
/* Estilos específicos para el dashboard */
.dashboard-container {
  background-color: #f9fafb;
}

/* Mejoras para gráficos */
canvas {
  max-height: 320px;
  border-radius: 0.5rem;
}

/* Asegurar que los gráficos sean responsivos */
@media (max-width: 768px) {
  canvas {
    max-height: 250px;
  }
}

/* Animaciones suaves para elementos interactivos */
.transition-colors {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Mejoras de accesibilidad */
button:focus-visible {
  outline: 2px solid rgb(34 197 94);
  outline-offset: 2px;
}

/* Estilos para elementos de carga */
.loading-overlay {
  background-color: rgba(249, 250, 251, 0.8);
  backdrop-filter: blur(2px);
}

/* Espaciado consistente */
.section-spacing {
  margin-bottom: 2rem;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}

@media (max-width: 640px) {
  .dashboard-header h1 {
    font-size: 1.875rem;
  }

  .dashboard-header p {
    font-size: 1rem;
  }
}

/* Estilos para elementos de estado */
.status-success {
  color: rgb(34 197 94);
}

.status-warning {
  color: rgb(245 158 11);
}

.status-error {
  color: rgb(239 68 68);
}

.status-info {
  color: rgb(59 130 246);
}
</style>
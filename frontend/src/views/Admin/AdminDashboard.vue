<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar Component -->
    <AdminSidebar 
      :brand-name="brandName" 
      :user-name="userName" 
      :user-role="userRole" 
      :current-route="$route.path"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick" 
      @logout="handleLogout" 
      @toggle-collapse="toggleSidebarCollapse" 
    />

    <!-- Main Content -->
    <div class="p-6 transition-all duration-300" :class="isSidebarCollapsed ? 'sm:ml-20' : 'sm:ml-64'" data-cy="admin-dashboard">
      <!-- Dashboard Header -->
      <div class="mb-8">
        <div class="bg-gradient-to-r from-white to-green-50 rounded-2xl border-2 border-gray-200 hover:shadow-xl hover:border-green-300 transition-all duration-300">
          <div class="px-8 py-6">
            <div class="flex-1">
              <div class="flex items-center gap-4">
                <div class="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-lg">
                  <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </div>
                <div>
                  <h1 class="text-3xl font-bold text-gray-900 mb-1">Dashboard de Administración</h1>
                  <p class="text-gray-600 text-base">Panel de control completo del sistema CacaoScan</p>
                </div>
              </div>
              <div class="flex items-center gap-2 ml-auto">
                <button
                  @click="refreshData"
                  :disabled="isRefreshing"
                  class="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-green-500"
                  data-cy="refresh-button"
                  title="Actualizar datos"
                >
                  <svg v-if="!isRefreshing" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                  </svg>
                  <svg v-else class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                  </svg>
                </button>
                <div v-if="isRefreshing" class="flex items-center gap-2 text-sm text-green-600">
                  <span>Actualizando...</span>
                </div>
                <div v-else-if="lastUpdateTime" class="text-xs text-gray-500">
                  Última actualización: {{ formatLastUpdate(lastUpdateTime) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- KPI Cards Component -->
      <div class="mb-8">
        <KPICards :cards="kpiCards" />
      </div>

      <!-- Charts Component -->
      <div class="mb-8">
        <DashboardCharts 
          :activity-chart-title="activityChartTitle" 
          :quality-chart-title="qualityChartTitle"
          :activity-chart-data="activityChartData" 
          :quality-chart-data="qualityChartData"
          :activity-chart-options="activityChartOptions" 
          :quality-chart-options="qualityChartOptions" 
          :loading="loading"
          :initial-activity-chart-type="activityChartType" 
          @activity-chart-type-change="handleActivityChartTypeChange"
          @activity-refresh="handleActivityRefresh" 
          @quality-refresh="handleQualityRefresh"
          @activity-click="handleActivityClick" 
          @quality-click="handleQualityClick" 
        />
      </div>

      <!-- Tables Component -->
      <div class="mb-8">
        <DashboardTables 
          :users-table-title="usersTableTitle" 
          :users-table-link="usersTableLink"
          :users-table-link-text="usersTableLinkText" 
          :activity-table-title="activityTableTitle"
          :activity-table-link="activityTableLink" 
          :activity-table-link-text="activityTableLinkText"
          :recent-users="recentUsers" 
          :recent-activities="recentActivities" 
          @view-user="handleViewUser"
          @edit-user="handleEditUser" 
        />
      </div>

      <!-- Alerts and Reports Component -->
      <div class="mb-8">
        <DashboardAlerts 
          :alerts-title="alertsTitle" 
          :no-alerts-message="noAlertsMessage" 
          :reports-title="reportsTitle"
          :reports-link="reportsLink" 
          :reports-link-text="reportsLinkText" 
          :total-reports-label="totalReportsLabel"
          :completed-reports-label="completedReportsLabel" 
          :generating-reports-label="generatingReportsLabel"
          :failed-reports-label="failedReportsLabel" 
          :alerts="alerts" 
          :report-stats="reportStats"
          @dismiss-alert="handleDismissAlert" 
        />
      </div>
    </div>
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, computed, watch, onMounted, onUnmounted, onActivated } from 'vue'

// 2. Vue router
import { useRouter, useRoute } from 'vue-router'

// 3. Components
import AdminSidebar from '@/components/layout/Common/Sidebar.vue'
import KPICards from '@/components/admin/AdminDashboardComponents/KPICards.vue'
import DashboardCharts from '@/components/admin/AdminDashboardComponents/DashboardCharts.vue'
import DashboardTables from '@/components/admin/AdminDashboardComponents/DashboardTables.vue'
import DashboardAlerts from '@/components/admin/AdminDashboardComponents/DashboardAlerts.vue'

// 4. Stores
import { useAuthStore } from '@/stores/auth'
import { useConfigStore } from '@/stores/config'
import { useAdminStore } from '@/stores/admin'

// 5. Composables
import { useWebSocket } from '@/composables/useWebSocket'

// 6. Utils
import Swal from 'sweetalert2'

// Router and stores
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const adminStore = useAdminStore()
const configStore = useConfigStore()

// WebSocket
let websocket = null
try {
  websocket = useWebSocket()
} catch (e) {
  }

// Reactive data
const loading = ref(false)
const isRefreshing = ref(false)
const lastUpdateTime = ref(null)
const stats = ref({})
const recentUsers = ref([])
const recentActivities = ref([])
const alerts = ref([])
const reportStats = ref({})
const selectedPeriod = ref('30')
const activityChartType = ref('line')
const isSidebarCollapsed = ref(false)

// Chart data
const activityData = ref({ labels: [], datasets: [] })
const qualityData = ref({ labels: [], datasets: [] })

// Computed properties
const brandName = computed(() => configStore.brandName)

const userName = computed(() => {
  const user = authStore.user
  if (!user) return 'Admin User'
  if (user.first_name && user.last_name) {
    return `${user.first_name} ${user.last_name}`.trim()
  }
  return user.username || 'Admin User'
})

const userRole = computed(() => {
  const role = authStore.userRole || 'Usuario'
  if (role === 'admin') return 'admin'
  if (role === 'farmer') return 'agricultor'
  return 'admin'
})

const kpiCards = computed(() => {
  if (!stats.value || Object.keys(stats.value).length === 0) {
    return [
      { id: 'users', value: 0, label: 'Usuarios Totales', iconPath: '', change: 0, changePeriod: 'esta semana', variant: 'primary', trend: { data: [], direction: 'stable' } },
      { id: 'fincas', value: 0, label: 'Fincas Registradas', iconPath: '', change: 0, changePeriod: 'esta semana', variant: 'success', trend: { data: [], direction: 'stable' } },
      { id: 'analyses', value: 0, label: 'Análisis Realizados', iconPath: '', change: 0, changePeriod: 'esta semana', variant: 'info', trend: { data: [], direction: 'stable' } },
      { id: 'quality', value: 0, label: 'Calidad Promedio', iconPath: '', suffix: '%', change: 0, changePeriod: 'vs mes anterior', variant: 'warning', trend: { data: [], direction: 'stable' } }
    ]
  }
  
  // Extract data from backend response structure
  const usersTotal = Number(stats.value?.users?.total) || Number(stats.value?.total_users) || 0
  const usersThisWeek = Number(stats.value?.users?.this_week) || 0
  const fincasTotal = Number(stats.value?.fincas?.total) || 0
  const fincasThisWeek = Number(stats.value?.fincas?.this_week) || 0
  const imagesTotal = Number(stats.value?.images?.total) || Number(stats.value?.total_images) || 0
  const imagesThisWeek = Number(stats.value?.images?.this_week) || 0
  
  // Debug logging
  if (usersTotal === 0 && stats.value?.users) {
    }
  
  // Calculate average quality from predictions
  let avgQuality = 0
  const confidence = stats.value?.predictions?.average_confidence
  if (confidence !== undefined && confidence !== null && Number(confidence) >= 0) {
    avgQuality = Math.round(Number(confidence) * 100)
  } else if (stats.value?.avg_quality !== undefined && stats.value?.avg_quality !== null) {
    avgQuality = Number(stats.value.avg_quality)
  }
  
  const qualityChange = 0
  
  return [
    {
      id: 'users',
      value: usersTotal,
      label: 'Usuarios Totales',
      iconPath: 'M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z',
      change: usersThisWeek,
      changePeriod: 'esta semana',
      variant: 'primary',
      trend: {
        data: [],
        direction: usersThisWeek > 0 ? 'up' : 'stable'
      }
    },
    {
      id: 'fincas',
      value: fincasTotal,
      label: 'Fincas Registradas',
      iconPath: 'M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z',
      fillRule: 'evenodd',
      clipRule: 'evenodd',
      change: fincasThisWeek,
      changePeriod: 'esta semana',
      variant: 'success',
      trend: {
        data: [],
        direction: fincasThisWeek > 0 ? 'up' : 'stable'
      }
    },
    {
      id: 'analyses',
      value: imagesTotal,
      label: 'Análisis Realizados',
      iconPath: 'M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z',
      fillRule: 'evenodd',
      clipRule: 'evenodd',
      change: imagesThisWeek,
      changePeriod: 'esta semana',
      variant: 'info',
      trend: {
        data: [],
        direction: imagesThisWeek > 0 ? 'up' : 'stable'
      }
    },
    {
      id: 'quality',
      value: avgQuality,
      label: 'Calidad Promedio',
      iconPath: 'M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z',
      suffix: '%',
      change: Math.round(qualityChange),
      changePeriod: 'vs mes anterior',
      variant: 'warning',
      trend: {
        data: [],
        direction: (() => {
          if (qualityChange > 0) return 'up'
          if (qualityChange < 0) return 'down'
          return 'stable'
        })()
      }
    }
  ]
})

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

// Watch stats for debugging
watch(() => stats.value, (newStats) => {
  }, { deep: true })

// Properties
const navbarTitle = ref('Dashboard de Administración')
const navbarSubtitle = ref('Panel de control completo del sistema CacaoScan')
const searchPlaceholder = ref('Buscar usuarios, análisis, reportes...')
const refreshButtonText = ref('Actualizar')
const searchQuery = ref('')

const activityChartTitle = ref('Actividad de Usuarios')
const qualityChartTitle = ref('Distribución de Calidad')

const usersTableTitle = ref('Usuarios Recientes')
const usersTableLink = ref('/admin/agricultores')
const usersTableLinkText = ref('Ver Todos')
const activityTableTitle = ref('Actividad Reciente')
const activityTableLink = ref('/admin/audit')
const activityTableLinkText = ref('Ver Auditoría')

const alertsTitle = ref('Alertas del Sistema')
const noAlertsMessage = ref('No hay alertas activas')
const reportsTitle = ref('Reportes Generados')
const reportsLink = ref('/admin/reports')
const reportsLinkText = ref('Gestionar Reportes')
const totalReportsLabel = ref('Total Reportes')
const completedReportsLabel = ref('Completados')
const generatingReportsLabel = ref('Generando')
const failedReportsLabel = ref('Fallidos')

// Functions
const toggleSidebarCollapse = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem('sidebarCollapsed', String(isSidebarCollapsed.value))
}

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
    isRefreshing.value = true
    const response = await adminStore.getGeneralStats()
    const data = response.data || {}
    
    // Merge data with defaults to ensure all expected properties exist
    const statsData = {
      users: data.users || { total: 0, this_week: 0, this_month: 0 },
      fincas: data.fincas || { total: 0, this_week: 0, this_month: 0 },
      images: data.images || { total: 0, this_week: 0, this_month: 0 },
      // Only set predictions default if not provided in data
      ...(data.predictions ? { predictions: data.predictions } : {}),
      activity_by_day: data.activity_by_day || { labels: [], data: [] },
      quality_distribution: data.quality_distribution || { excelente: 0, buena: 0, regular: 0, baja: 0 },
      ...data  // Spread data last to allow custom properties like avg_quality to override
    }
    
    // Reassign to ensure reactivity - completely replace to trigger computed updates
    stats.value = statsData
    lastUpdateTime.value = new Date()
    
    updateActivityChartFromStats()
    updateQualityChartFromStats()
  } catch (error) {
    // Set default values but still throw to let loadDashboardData handle the error
    stats.value = {
      users: { total: 0 },
      fincas: { total: 0 },
      images: { total: 0 },
      predictions: { average_confidence: 0 }
    }
    throw error
  } finally {
    isRefreshing.value = false
  }
}

const processUserData = (user) => {
  // Extract name from first_name and last_name, fallback to username or email
  const firstName = user.first_name || ''
  const lastName = user.last_name || ''
  const fullName = `${firstName} ${lastName}`.trim()
  const displayName = fullName || user.username || user.email?.split('@')[0] || 'Usuario'
  
  return {
    id: user.id,
    username: user.username || user.email?.split('@')[0] || 'Usuario',
    email: user.email || '',
    first_name: firstName,
    last_name: lastName,
    full_name: displayName,
    role: user.role || 'farmer',
    is_active: user.is_active !== false,
    date_joined: user.date_joined || user.created_at
  }
}

const loadRecentUsers = async () => {
  try {
    isRefreshing.value = true
    const response = await adminStore.getRecentUsers(5)
    const data = response.data
    
    let usersArray = []
    if (Array.isArray(data)) {
      usersArray = data
    } else if (data?.results && Array.isArray(data.results)) {
      usersArray = data.results
    } else if (data?.data && Array.isArray(data.data)) {
      usersArray = data.data
    }
    
    recentUsers.value = usersArray.map(processUserData)
    
    lastUpdateTime.value = new Date()
  } catch (error) {
    recentUsers.value = []
  } finally {
    isRefreshing.value = false
  }
}

const getActionDisplay = (activity) => {
  // Check if display is already provided
  if (activity.accion_display || activity.action_display) {
    return activity.accion_display || activity.action_display
  }
  
  // Map action to display text
  const action = activity.accion || activity.action
  const actionMap = {
    'create': 'Crear',
    'update': 'Actualizar',
    'delete': 'Eliminar',
    'view': 'Ver',
    'login': 'Login',
    'logout': 'Logout',
    'read': 'Leer'
  }
  
  return actionMap[action] || action || 'Desconocida'
}

const processActivityData = (activity) => {
  return {
    id: activity.id,
    usuario: activity.usuario || activity.user?.username || activity.username || 'Anónimo',
    accion: activity.accion || activity.action || 'unknown',
    accion_display: getActionDisplay(activity),
    modelo: activity.modelo || activity.model || activity.content_type || 'N/A',
    timestamp: activity.timestamp || activity.created_at || activity.date || new Date().toISOString(),
    descripcion: activity.descripcion || activity.description || '',
    ip_address: activity.ip_address || activity.ip || ''
  }
}

const loadRecentActivities = async () => {
  try {
    isRefreshing.value = true
    const response = await adminStore.getRecentActivities(20)
    const data = response.data || {}
    let activitiesArray = []
    if (Array.isArray(data)) {
      activitiesArray = data
      } else if (data?.results && Array.isArray(data.results)) {
      activitiesArray = data.results
      } else if (data?.data && Array.isArray(data.data)) {
      activitiesArray = data.data
      } else {
      }
    
    recentActivities.value = activitiesArray.map(processActivityData)
    lastUpdateTime.value = new Date()
  } catch (error) {
    recentActivities.value = []
  } finally {
    isRefreshing.value = false
  }
}

const processAlertData = (notification) => {
  const typeMapping = {
    'success': 'success',
    'warning': 'warning',
    'error': 'error',
    'info': 'info',
    'critical': 'error'
  }
  
  return {
    id: notification.id,
    title: notification.titulo || notification.title || 'Alerta',
    message: notification.mensaje || notification.message || '',
    type: typeMapping[notification.tipo?.toLowerCase()] || notification.tipo || 'info',
    created_at: notification.fecha_creacion || notification.created_at || notification.fecha_creacion || new Date().toISOString(),
    leida: notification.leida || false
  }
}

const loadAlerts = async () => {
  try {
    isRefreshing.value = true
    const response = await adminStore.getSystemAlerts()
    const data = response.data || {}
    
    let notificationsArray = []
    if (Array.isArray(data)) {
      notificationsArray = data
    } else if (data?.results && Array.isArray(data.results)) {
      notificationsArray = data.results
    } else if (data?.data && Array.isArray(data.data)) {
      notificationsArray = data.data
    }
    
    alerts.value = notificationsArray.map(processAlertData)
    lastUpdateTime.value = new Date()
  } catch (error) {
    alerts.value = []
  } finally {
    isRefreshing.value = false
  }
}

const loadReportStats = async () => {
  try {
    isRefreshing.value = true
    const response = await adminStore.getReportStats()
    const data = response.data || {}
    
    reportStats.value = {
      total_reportes: data.total_reportes || 0,
      reportes_completados: data.reportes_completados || 0,
      reportes_generando: data.reportes_generando || 0,
      reportes_fallidos: data.reportes_fallidos || 0,
      ...data
    }
    
    lastUpdateTime.value = new Date()
  } catch (error) {
    reportStats.value = {
      total_reportes: 0,
      reportes_completados: 0,
      reportes_generando: 0,
      reportes_fallidos: 0
    }
  } finally {
    isRefreshing.value = false
  }
}

const updateQualityChartFromStats = () => {
  const quality = stats.value?.quality_distribution || { excelente: 0, buena: 0, regular: 0, baja: 0 }
  
  // Ensure we always have valid data for the chart
  const excelente = Number(quality.excelente) || 0
  const buena = Number(quality.buena) || 0
  const regular = Number(quality.regular) || 0
  const baja = Number(quality.baja) || 0
  
  // If all values are zero, set a default value to show the chart
  const total = excelente + buena + regular + baja
  const defaultData = total === 0 ? [1, 0, 0, 0] : [excelente, buena, regular, baja]
  
  qualityData.value = {
    labels: ['Excelente', 'Buena', 'Regular', 'Baja'],
    datasets: [{
      data: defaultData,
      backgroundColor: [
        '#22c55e',
        '#3b82f6',
        '#f59e0b',
        '#ef4444'
      ],
      borderWidth: 2,
      borderColor: '#ffffff'
    }]
  }
}

const loadQualityData = async () => {
  try {
    if (stats.value?.quality_distribution) {
      updateQualityChartFromStats()
      return
    }
    
    const response = await adminStore.getQualityDistribution()
    const quality = response.data || { excelente: 0, buena: 0, regular: 0, baja: 0 }
    
    // Update stats with quality distribution if available
    if (quality && (quality.excelente !== undefined || quality.buena !== undefined)) {
      stats.value = {
        ...stats.value,
        quality_distribution: quality
      }
    }
    
    updateQualityChartFromStats()
  } catch (error) {
    updateQualityChartFromStats()
  }
}

const updateActivityChartFromStats = () => {
  const activity = stats.value?.activity_by_day || { labels: [], data: [] }
  // Ensure we always have valid data for the chart
  const labels = activity.labels && activity.labels.length > 0 
    ? activity.labels 
    : ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
  
  const data = activity.data && activity.data.length > 0 
    ? activity.data 
    : [0, 0, 0, 0, 0, 0, 0]
  
  activityData.value = {
    labels,
    datasets: [{
      label: 'Actividad del Sistema',
      data,
      borderColor: '#22c55e',
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointHoverRadius: 6,
      pointBackgroundColor: '#22c55e',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2
    }]
  }
  
  }

const updateActivityChart = async () => {
  try {
    if (stats.value?.activity_by_day && stats.value.activity_by_day.labels && stats.value.activity_by_day.labels.length > 0) {
      updateActivityChartFromStats()
      return
    }
    
    const response = await adminStore.getActivityData(selectedPeriod.value)
    if (response.data && response.data.results && Array.isArray(response.data.results)) {
      // Process activity logs to create chart data
      const activities = response.data.results
      const last7Days = []
      const today = new Date()
      
      // Generate labels for last 7 days
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(date.getDate() - i)
        last7Days.push(date.toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric' }))
      }
      
      // Count activities per day
      const activityCounts = new Array(7).fill(0)
      activities.forEach(activity => {
        if (activity.timestamp || activity.created_at) {
          const activityDate = new Date(activity.timestamp || activity.created_at)
          const daysDiff = Math.floor((today - activityDate) / (1000 * 60 * 60 * 24))
          if (daysDiff >= 0 && daysDiff < 7) {
            activityCounts[6 - daysDiff]++
          }
        }
      })
      
      // Update stats with processed activity data
      stats.value = {
        ...stats.value,
        activity_by_day: {
          labels: last7Days,
          data: activityCounts
        }
      }
    }
    
    updateActivityChartFromStats()
  } catch (error) {
    updateActivityChartFromStats()
  }
}

const refreshData = () => {
  loadDashboardData()
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

// Utility functions
const formatLastUpdate = (date) => {
  if (!date) return 'Nunca'
  const now = new Date()
  const updateDate = new Date(date)
  const diffMs = now - updateDate
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  
  if (diffSecs < 5) return 'Ahora'
  if (diffSecs < 60) return `Hace ${diffSecs}s`
  if (diffMins < 60) return `Hace ${diffMins}m`
  return updateDate.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

// Event handlers
const handleMenuClick = (menuItem) => {
  if (menuItem.route) {
    router.push(menuItem.route)
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
  } catch (error) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo cerrar la sesión'
    })
  }
}

const handleActivityChartTypeChange = (chartType) => {
  activityChartType.value = chartType
  updateActivityChart()
}

const handleActivityRefresh = () => {
  refreshActivityData()
}

const handleQualityRefresh = () => {
  refreshQualityData()
}

const handleActivityClick = (event) => {
  }

const handleQualityClick = (event) => {
  }

const handleViewUser = (userId) => {
  router.push(`/admin/users/${userId}`)
}

const handleEditUser = (userId) => {
  router.push(`/admin/users/${userId}/edit`)
}

const handleDismissAlert = (alertId) => {
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
      Swal.fire('Descartada', 'La alerta ha sido descartada', 'success')
    }
  })
}

// Real-time updates
let refreshInterval = null
let statsInterval = null
let quickRefreshInterval = null

const QUICK_REFRESH_INTERVAL = 3000
const REFRESH_INTERVAL = 8000
const STATS_INTERVAL = 25000

const setupWebSocketListeners = () => {
  if (!websocket) return

  websocket.on?.('audit-stats-update', (data) => {
    if (data) {
      if (data.users) stats.value.users = { ...stats.value.users, ...data.users }
      if (data.images) stats.value.images = { ...stats.value.images, ...data.images }
      if (data.fincas) stats.value.fincas = { ...stats.value.fincas, ...data.fincas }
      updateActivityChartFromStats()
      updateQualityChartFromStats()
    }
  })

  websocket.on?.('audit-activity', (data) => {
    const processed = processActivityData(data)
    recentActivities.value = [processed, ...recentActivities.value].slice(0, 20)
  })

  websocket.on?.('notification-received', (data) => {
    const processed = processAlertData(data)
    alerts.value = [processed, ...alerts.value].slice(0, 10)
  })

  websocket.on?.('user-stats-update', (data) => {
    if (data?.users) {
      stats.value.users = { ...stats.value.users, ...data.users }
    }
  })
}

const startPollingUpdates = () => {
  quickRefreshInterval = setInterval(() => {
    Promise.all([
      loadAlerts(),
      loadRecentActivities()
    ]).catch(err => {
      })
  }, QUICK_REFRESH_INTERVAL)

  refreshInterval = setInterval(() => {
    Promise.all([
      loadRecentUsers(),
      loadReportStats()
    ]).catch(err => {
      })
  }, REFRESH_INTERVAL)

  statsInterval = setInterval(() => {
    Promise.all([
      loadStats(),
      loadQualityData(),
      updateActivityChart()
    ]).catch(err => {
      })
  }, STATS_INTERVAL)
}

const setupRealtimeUpdates = () => {
  if (websocket && websocket.hasAnyConnection?.value) {
    setupWebSocketListeners()
    startPollingUpdates()
  } else {
    startPollingUpdates()
  }
}

const stopAutoRefresh = () => {
  if (quickRefreshInterval) {
    clearInterval(quickRefreshInterval)
    quickRefreshInterval = null
  }
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
  if (statsInterval) {
    clearInterval(statsInterval)
    statsInterval = null
  }

  if (websocket) {
    websocket.off?.('audit-stats-update')
    websocket.off?.('audit-activity')
    websocket.off?.('notification-received')
    websocket.off?.('user-stats-update')
  }
}

// Función para inicializar el dashboard
const initializeDashboard = async () => {
  if (!authStore.isAdmin) {
    router.push('/acceso-denegado')
    return
  }

  await loadDashboardData()
  
  if (websocket && authStore.user?.id) {
    try {
      await websocket.connect()
    } catch (error) {
      }
  }
  
  setupRealtimeUpdates()
}

// Lifecycle
onMounted(async () => {
  await initializeDashboard()
})

// Si el componente está dentro de keep-alive, se ejecuta cuando se activa
onActivated(async () => {
  // Recargar datos cuando se vuelve a la vista
  await initializeDashboard()
})

// Watch para detectar cambios de ruta
watch(() => route.path, async (newPath, oldPath) => {
  // Si volvemos al dashboard desde otra ruta, recargar datos
  if (newPath === '/admin/dashboard' && oldPath !== newPath) {
    await initializeDashboard()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
/* Solo estilos específicos que no están en Tailwind */
canvas {
  max-height: 320px;
  border-radius: 0.5rem;
}

@media (max-width: 768px) {
  canvas {
    max-height: 250px;
  }
}
</style>

<template>
  <div class="flex min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar
      :brand-name="'CacaoScan'"
      :user-name="farmerName"
      :user-role="computedUserRole"
      :current-route="route.path"
      :active-section="activeSection"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="logout"
      @toggle-collapse="toggleSidebarCollapse"
    />

    <!-- Main Content -->
    <main class="min-h-screen w-full p-8 overflow-y-auto" :class="isSidebarCollapsed ? 'ml-20' : 'ml-64'">
      <!-- Overview Section -->
      <div v-if="activeSection === 'overview'" class="max-w-full space-y-6">
        <WelcomeHeader :farmer-name="farmerName" />
        
        <!-- Quality Overview Card - Compact -->
        <QualityOverviewCard
          :quality="qualityStats?.averageQuality || 0"
          :classification="qualityClassification"
          :trend="qualityTrend"
        />
        
        <!-- Stats Cards - 4 cards in a row -->
        <StatsCards 
          :total-fincas="farmerStats.totalFincas"
          :total-lotes="farmerStats.totalLotes"
          :total-batches="formattedStats.totalBatches"
          :total-analyses="totalImages"
          :average-quality="qualityStats?.averageQuality || 0"
        />
        
        <!-- Quality Stats Card -->
        <QualityStatsCard
          :average-quality="qualityStats?.averageQuality || 0"
          :total-analyses="totalImages"
          :processing-rate="Math.round(processingRate * 100)"
          :processed-images="processedImages"
          :total-images="totalImages"
          :average-defects="Math.round((1 - averageConfidence) * 100)"
          :average-confidence="Math.round(averageConfidence * 100)"
          :processed-today="stats?.processed_today || 0"
          :processed-this-week="stats?.processed_this_week || 0"
          :processed-this-month="stats?.processed_this_month || 0"
        />
        
        <!-- Smart Alerts -->
        <SmartAlerts
          :alerts="alerts"
          :loading="alertsLoading"
          @action-click="handleAlertAction"
        />
        
        <!-- Grid: Recent Activity and Quick Actions -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RecentActivity 
            :recent-analyses="recentAnalyses" 
            @select-analysis="handleSelectAnalysis"
          />
          <QuickActions 
            :has-critical-alerts="highPriorityAlerts.length > 0"
            :critical-alerts-count="highPriorityAlerts.length"
            @nuevo-analisis="handleNuevoAnalisis"
            @generar-reporte="handleGenerarReporte"
            @ver-alertas="scrollToAlerts"
            @ver-recomendaciones="scrollToRecommendations"
          />
        </div>
        
        <!-- Agricultural Map -->
        <AgriculturalMap
          :fincas="fincasWithQuality"
          :loading="fincasLoading"
        />
        
        <!-- Quality Trend Chart -->
        <QualityTrendChart
          :chart-data="trendChartData"
          :loading="trendLoading"
          @period-change="handlePeriodChange"
        />
        
        <!-- Top Performance -->
        <TopPerformance
          :top-fincas="topFincasData"
          :top-lotes="topLotesData"
          :loading="topPerformanceLoading"
        />
        
        <!-- Grid: Defects Breakdown and Smart Recommendations -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DefectsBreakdown
            :defects-data="defectsData"
            :loading="defectsLoading"
          />
          <SmartRecommendations
            :recommendations="recommendations"
            :loading="recommendationsLoading"
          />
        </div>
        
        <!-- Production Summary -->
        <ProductionSummary
          :summary="productionSummary"
          :loading="productionLoading"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 2. Vue router
import { useRoute, useRouter } from 'vue-router'

// 3. Stores
import { useAuthStore } from '@/stores/auth'

// 4. Services
import { getFincas } from '@/services/fincasApi'
import { getLotes } from '@/services/lotesApi'

// 5. Composables
import { useImageStats } from '@/composables/useImageStats'
import { useQualityData } from '@/composables/useQualityData'
import { useAlerts } from '@/composables/useAlerts'
import { useRecommendations } from '@/composables/useRecommendations'

// 6. Components
import Sidebar from '@/components/layout/Common/Sidebar.vue'
import WelcomeHeader from '@/components/agricultor/WelcomeHeader.vue'
import StatsCards from '@/components/agricultor/StatsCards.vue'
import RecentActivity from '@/components/agricultor/RecentActivity.vue'
import QuickActions from '@/components/agricultor/QuickActions.vue'
import QualityOverviewCard from '@/components/agricultor/QualityOverviewCard.vue'
import QualityStatsCard from '@/components/agricultor/QualityStatsCard.vue'
import SmartAlerts from '@/components/agricultor/SmartAlerts.vue'
import AgriculturalMap from '@/components/agricultor/AgriculturalMap.vue'
import QualityTrendChart from '@/components/agricultor/QualityTrendChart.vue'
import TopPerformance from '@/components/agricultor/TopPerformance.vue'
import DefectsBreakdown from '@/components/agricultor/DefectsBreakdown.vue'
import SmartRecommendations from '@/components/agricultor/SmartRecommendations.vue'
import ProductionSummary from '@/components/agricultor/ProductionSummary.vue'

// Router & Route
const router = useRouter()
const route = useRoute()

// Stores
const authStore = useAuthStore()

// Composables
const { 
  stats, 
  loading, 
  error, 
  fetchStats, 
  fetchImages, 
  generateReport,
  totalImages,
  processedImages,
  processingRate,
  averageConfidence,
  averageDimensions,
  regionStats,
  topFincas
} = useImageStats()

const {
  qualityStats,
  fincasData,
  loading: qualityLoading,
  fetchQualityStats,
  fetchFincasWithQuality,
  qualityClassification,
  qualityTrend
} = useQualityData()

const {
  alerts,
  loading: alertsLoading,
  generateAlerts,
  highPriorityAlerts
} = useAlerts()

const {
  recommendations,
  loading: recommendationsLoading,
  generateRecommendations
} = useRecommendations()

// State
const isSidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')

// Initialize activeSection from query parameter if present
const sectionParam = route.query.section
const activeSection = ref(sectionParam || 'overview')

// Datos de análisis recientes (ahora desde API)
const recentAnalyses = ref([])
const imagesLoading = ref(false)

// Estadísticas del agricultor
const farmerStats = ref({
  totalFincas: 0,
  totalLotes: 0
})
const loadingStats = ref(false)

// New state for additional data
const fincasWithQuality = ref([])
const fincasLoading = ref(false)
const trendChartData = ref([])
const trendLoading = ref(false)
const selectedPeriod = ref('30')
const topFincasData = ref([])
const topLotesData = ref([])
const topPerformanceLoading = ref(false)
const defectsData = ref([])
const defectsLoading = ref(false)
const productionSummary = ref({
  totalLotes: 0,
  avgImagesPerLote: 0,
  successRate: 0,
  avgProcessingTime: '0s'
})
const productionLoading = ref(false)

// Computed
const farmerName = computed(() => authStore.userFullName || 'Usuario')

// Normalize user role for sidebar (convert 'farmer' to 'agricultor')
const computedUserRole = computed(() => {
  const role = authStore.userRole || 'farmer'
  // Convert 'farmer' to 'agricultor' for sidebar compatibility
  if (role === 'farmer') {
    return 'agricultor'
  }
  return role === 'admin' ? 'admin' : 'agricultor'
})

// Función helper para calcular cambio porcentual
const calculatePercentageChange = (current, previous) => {
  if (!previous || previous === 0) return current > 0 ? '+100%' : '0%'
  const change = ((current - previous) / previous) * 100
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(1)}%`
}

const formattedStats = computed(() => {
  // Pendiente: Obtener estadísticas del período anterior desde el backend
  // Por ahora usamos valores estáticos; cuando esté disponible el endpoint:
  // const stats = await api.get('/agricultores/stats/?period=current,previous')
  const previousStats = {
    batches: 0, // stats.previous.total_batches
    quality: 0, // stats.previous.avg_quality
    defects: 0  // stats.previous.defect_rate
  }
  
  return {
    totalBatches: totalImages.value,
    batchesChange: calculatePercentageChange(totalImages.value, previousStats.batches),
    avgQuality: Math.round(averageConfidence.value * 100),
    qualityChange: calculatePercentageChange(Math.round(averageConfidence.value * 100), previousStats.quality),
    defectRate: Math.round((1 - averageConfidence.value) * 100 * 10) / 10,
    defectChange: calculatePercentageChange(
      Math.round((1 - averageConfidence.value) * 100 * 10) / 10,
      previousStats.defects
    )
  }
})

// Functions
const loadRecentAnalyses = async () => {
  imagesLoading.value = true
  try {
    const data = await fetchImages(1, { page_size: 5 })
    if (data && data.results && Array.isArray(data.results)) {
      recentAnalyses.value = data.results.map(image => ({
        id: `CAC-${image.id}`,
        status: image.processed ? 'completed' : 'pending',
        statusLabel: image.processed ? 'Completado' : 'Pendiente',
        quality: image.prediction ? Math.round(image.prediction.average_confidence * 100) : 0,
        defects: image.prediction ? Math.round((1 - image.prediction.average_confidence) * 100 * 10) / 10 : 0,
        avgSize: image.prediction ? Math.round((image.prediction.alto_mm + image.prediction.ancho_mm + image.prediction.grosor_mm) / 3 * 10) / 10 : 0,
        date: new Date(image.created_at).toLocaleDateString('es-ES', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        })
      }))
    } else {
      recentAnalyses.value = []
    }
  } catch (err) {
    recentAnalyses.value = []
  } finally {
    imagesLoading.value = false
  }
}

const handleGenerateReport = async (reportType) => {
  await generateReport(reportType, {})
}

const loadFarmerStats = async () => {
  loadingStats.value = true
  try {
    // Cargar fincas del agricultor
    const fincasResponse = await getFincas({ activa: true })
    const totalFincas = fincasResponse.count || (fincasResponse.results ? fincasResponse.results.length : 0)
    
    // Cargar lotes del agricultor
    // Use 'activa' parameter as the backend expects (line 175 in lote_views.py)
    // But we need to get the raw response to preserve 'count'
    const api = (await import('@/services/api')).default
    const lotesResponse = await api.get('/lotes/', { params: { activa: true } })
    
    // Extract count from paginated response
    // The response should have 'count' for paginated responses
    const totalLotes = lotesResponse.data?.count !== undefined ? lotesResponse.data.count : 
                       (lotesResponse.data?.results ? lotesResponse.data.results.length : 
                       (Array.isArray(lotesResponse.data) ? lotesResponse.data.length : 0))
    
    farmerStats.value = {
      totalFincas,
      totalLotes
    }
  } catch (error) {
    console.error('[AgricultorDashboard] Error loading farmer stats:', error)
    farmerStats.value = {
      totalFincas: 0,
      totalLotes: 0
    }
  } finally {
    loadingStats.value = false
  }
}

const loadFincasWithQuality = async () => {
  fincasLoading.value = true
  try {
    const fincas = await fetchFincasWithQuality()
    fincasWithQuality.value = fincas
  } catch (err) {
    console.error('[AgricultorDashboard] Error loading fincas with quality:', err)
    fincasWithQuality.value = []
  } finally {
    fincasLoading.value = false
  }
}

const loadTrendData = async (period = '30') => {
  trendLoading.value = true
  try {
    const api = (await import('@/services/api')).default
    const daysAgo = Number.parseInt(period, 10)
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - daysAgo)
    
    const response = await api.get('/images/', {
      params: {
        page: 1,
        page_size: 100,
        ordering: '-created_at',
        created_at__gte: startDate.toISOString().split('T')[0]
      }
    })
    
    const images = response.data?.results || []
    
    // Group by date and calculate averages
    const groupedByDate = {}
    images.forEach(image => {
      if (image.prediction) {
        const date = new Date(image.created_at).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' })
        if (!groupedByDate[date]) {
          groupedByDate[date] = { quality: [], defects: [] }
        }
        const quality = image.prediction.average_confidence * 100
        const defects = (1 - image.prediction.average_confidence) * 100
        groupedByDate[date].quality.push(quality)
        groupedByDate[date].defects.push(defects)
      }
    })
    
    trendChartData.value = Object.entries(groupedByDate).map(([date, data]) => ({
      date,
      quality: data.quality.reduce((a, b) => a + b, 0) / data.quality.length,
      defects: data.defects.reduce((a, b) => a + b, 0) / data.defects.length
    })).sort((a, b) => new Date(a.date) - new Date(b.date))
  } catch (err) {
    console.error('[AgricultorDashboard] Error loading trend data:', err)
    trendChartData.value = []
  } finally {
    trendLoading.value = false
  }
}

const loadTopPerformance = async () => {
  topPerformanceLoading.value = true
  try {
    // Load top fincas
    const fincas = await fetchFincasWithQuality()
    topFincasData.value = fincas
      .filter(f => f.quality > 0)
      .map(f => ({
        ...f,
        defectRate: (1 - f.quality / 100) * 100
      }))
      .sort((a, b) => b.quality - a.quality)
      .slice(0, 3)
    
    // Load top lotes
    const api = (await import('@/services/api')).default
    const imagesResponse = await api.get('/images/', {
      params: {
        page: 1,
        page_size: 50,
        ordering: '-created_at'
      }
    })
    
    const images = imagesResponse.data?.results || []
    const lotesMap = {}
    
    images.forEach(image => {
      if (image.lote_id && image.prediction) {
        const loteId = image.lote_id
        if (!lotesMap[loteId]) {
          lotesMap[loteId] = {
            id: loteId,
            codigo: `CAC-${loteId}`,
            quality: [],
            date: new Date(image.created_at).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' })
          }
        }
        lotesMap[loteId].quality.push(image.prediction.average_confidence * 100)
      }
    })
    
    topLotesData.value = Object.values(lotesMap)
      .map(lote => ({
        ...lote,
        quality: lote.quality.reduce((a, b) => a + b, 0) / lote.quality.length
      }))
      .sort((a, b) => b.quality - a.quality)
      .slice(0, 3)
  } catch (err) {
    console.error('[AgricultorDashboard] Error loading top performance:', err)
    topFincasData.value = []
    topLotesData.value = []
  } finally {
    topPerformanceLoading.value = false
  }
}

const loadDefectsData = async () => {
  defectsLoading.value = true
  try {
    // TODO: When backend provides specific defect types, use them
    // For now, we'll use a placeholder structure
    const api = (await import('@/services/api')).default
    const statsResponse = await api.get('/images/stats/')
    const avgConfidence = statsResponse.data?.average_confidence || 0
    const defectRate = (1 - avgConfidence) * 100
    
    // Placeholder data structure - replace when backend provides actual defect breakdown
    defectsData.value = [
      {
        type: 'fermentation',
        label: 'Fermentación incorrecta',
        percentage: Math.round(defectRate * 0.4),
        color: 'red'
      },
      {
        type: 'insects',
        label: 'Daño por insectos',
        percentage: Math.round(defectRate * 0.3),
        color: 'orange'
      },
      {
        type: 'humidity',
        label: 'Humedad',
        percentage: Math.round(defectRate * 0.2),
        color: 'yellow'
      },
      {
        type: 'broken',
        label: 'Granos partidos',
        percentage: Math.round(defectRate * 0.1),
        color: 'purple'
      }
    ].filter(d => d.percentage > 0)
  } catch (err) {
    console.error('[AgricultorDashboard] Error loading defects data:', err)
    defectsData.value = []
  } finally {
    defectsLoading.value = false
  }
}

const loadProductionSummary = async () => {
  productionLoading.value = true
  try {
    const api = (await import('@/services/api')).default
    const statsResponse = await api.get('/images/stats/')
    const stats = statsResponse.data || {}
    
    // Calculate monthly lotes (simplified - count unique lotes from recent images)
    const imagesResponse = await api.get('/images/', {
      params: {
        page: 1,
        page_size: 100,
        ordering: '-created_at'
      }
    })
    
    const images = imagesResponse.data?.results || []
    const thisMonth = new Date()
    thisMonth.setDate(1)
    const thisMonthImages = images.filter(img => new Date(img.created_at) >= thisMonth)
    const uniqueLotes = new Set(thisMonthImages.map(img => img.lote_id).filter(Boolean))
    
    const totalImages = stats.total_images || 0
    const processedImages = stats.processed_images || 0
    const avgProcessingTime = stats.average_processing_time_ms || 0
    
    productionSummary.value = {
      totalLotes: uniqueLotes.size,
      avgImagesPerLote: uniqueLotes.size > 0 ? Math.round(thisMonthImages.length / uniqueLotes.size) : 0,
      successRate: totalImages > 0 ? Math.round((processedImages / totalImages) * 100) : 0,
      avgProcessingTime: avgProcessingTime > 0 ? `${Math.round(avgProcessingTime / 1000)}s` : '0s'
    }
  } catch (err) {
    console.error('[AgricultorDashboard] Error loading production summary:', err)
    productionSummary.value = {
      totalLotes: 0,
      avgImagesPerLote: 0,
      successRate: 0,
      avgProcessingTime: '0s'
    }
  } finally {
    productionLoading.value = false
  }
}

const handlePeriodChange = (period) => {
  selectedPeriod.value = period
  loadTrendData(period)
}

const handleAlertAction = (action) => {
  if (action.route) {
    router.push(action.route)
  }
}

const handleGenerarReporte = async () => {
  try {
    await generateReport('monthly', {})
  } catch (err) {
    console.error('[AgricultorDashboard] Error generating report:', err)
  }
}

const scrollToAlerts = () => {
  const alertsElement = document.querySelector('[data-section="alerts"]')
  if (alertsElement) {
    alertsElement.scrollIntoView({ behavior: 'smooth' })
  }
}

const scrollToRecommendations = () => {
  const recommendationsElement = document.querySelector('[data-section="recommendations"]')
  if (recommendationsElement) {
    recommendationsElement.scrollIntoView({ behavior: 'smooth' })
  }
}

const refreshData = async () => {
  await Promise.all([
    fetchStats(),
    loadRecentAnalyses(),
    loadFarmerStats(),
    fetchQualityStats(),
    loadFincasWithQuality(),
    generateAlerts(),
    generateRecommendations(),
    loadTrendData(selectedPeriod.value),
    loadTopPerformance(),
    loadDefectsData(),
    loadProductionSummary()
  ])
}

const handleImageSelected = (image) => {
  // Image selected handler
}

const handleSelectAnalysis = (analysis) => {
  // Extraer el ID del formato CAC-{id}
  const imageId = analysis.id.replace('CAC-', '')
  // Navegar a la vista de detalle del análisis
  router.push({ 
    name: 'DetalleAnalisis', 
    params: { id: imageId } 
  })
}

const handleNuevoAnalisis = () => {
  router.push('/analisis')
    .catch(() => {
      router.push({ name: 'Analisis' })
    })
}

const handleGestionarFincas = () => {
  // Navegar a la vista de gestión de fincas
  router.push({ name: 'Fincas' })
}

const checkScreenSize = () => {
  if (globalThis.innerWidth <= 768) {
    isSidebarCollapsed.value = true
    localStorage.setItem('sidebarCollapsed', 'true')
  }
}

const setActiveSection = (section) => {
  activeSection.value = section
}

const handleMenuClick = (item) => {
  if (item.route && item.route !== null) {
    // If navigating to the same route, just update the activeSection
    if (route.path === item.route) {
      activeSection.value = 'overview'
    } else {
      router.push(item.route)
    }
  } else {
    // For internal sections without routes, just update activeSection
    activeSection.value = item.id
  }
}

const toggleSidebarCollapse = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value)
}

const logout = async () => {
  try {
    await authStore.logout()
  } catch (error) {
    authStore.clearAll()
  }
}

// Lifecycle
onMounted(async () => {
  checkScreenSize()
  globalThis.addEventListener('resize', checkScreenSize)
  
  await refreshData()
})

onUnmounted(() => {
  globalThis.removeEventListener('resize', checkScreenSize)
})
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>

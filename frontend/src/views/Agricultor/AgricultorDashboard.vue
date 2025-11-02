<template>
  <div class="flex min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar
      :brand-name="'CacaoScan'"
      :user-name="farmerName"
      :user-role="'agricultor'"
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
      <div v-if="activeSection === 'overview'" class="max-w-full">
        <WelcomeHeader :farmer-name="farmerName" />
        
        <StatsCards 
          :total-batches="formattedStats.totalBatches"
          :avg-quality="formattedStats.avgQuality"
          :defect-rate="formattedStats.defectRate"
        />
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <RecentActivity 
            :recent-analyses="recentAnalyses" 
            @select-analysis="handleSelectAnalysis"
          />
          <QuickActions 
            @nuevo-analisis="handleNuevoAnalisis"
            @gestionar-fincas="handleGestionarFincas"
          />
        </div>
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

// 4. Composables
import { useImageStats } from '@/composables/useImageStats'

// 5. Components
import Sidebar from '@/components/layout/Common/Sidebar.vue'
import ImageHistoryCard from '@/components/dashboard/ImageHistoryCard.vue'
import WelcomeHeader from '@/components/agricultor/WelcomeHeader.vue'
import StatsCards from '@/components/agricultor/StatsCards.vue'
import RecentActivity from '@/components/agricultor/RecentActivity.vue'
import QuickActions from '@/components/agricultor/QuickActions.vue'

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

// State
const isSidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')

// Initialize activeSection from query parameter if present
const sectionParam = route.query.section
const activeSection = ref(sectionParam || 'overview')

// Datos de análisis recientes (ahora desde API)
const recentAnalyses = ref([])
const imagesLoading = ref(false)

// Computed
const farmerName = computed(() => authStore.userFullName || 'Usuario')

const formattedStats = computed(() => ({
  totalBatches: totalImages.value,
  batchesChange: '+0%', // TODO: Calcular cambio porcentual
  avgQuality: Math.round(averageConfidence.value * 100),
  qualityChange: '+0%', // TODO: Calcular cambio porcentual
  defectRate: Math.round((1 - averageConfidence.value) * 100 * 10) / 10,
  defectChange: '+0%' // TODO: Calcular cambio porcentual
}))

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
    console.error('Error loading recent analyses:', err)
    recentAnalyses.value = []
  } finally {
    imagesLoading.value = false
  }
}

const handleGenerateReport = async (reportType) => {
  const success = await generateReport(reportType, {})
  if (success) {
    console.log(`Reporte ${reportType} generado exitosamente`)
  }
}

const refreshData = async () => {
  await Promise.all([
    fetchStats(),
    loadRecentAnalyses()
  ])
}

const handleImageSelected = (image) => {
  console.log('Imagen seleccionada:', image)
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
  // Navegar a la vista de análisis de predicción
  router.push({ name: 'Prediction' })
}

const handleGestionarFincas = () => {
  // Navegar a la vista de gestión de fincas
  router.push({ name: 'Fincas' })
}

const checkScreenSize = () => {
  if (window.innerWidth <= 768) {
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
    console.error('Error al cerrar sesión:', error)
    authStore.clearAll()
  }
}

// Lifecycle
onMounted(async () => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  
  await Promise.all([
    fetchStats(),
    loadRecentAnalyses()
  ])
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>

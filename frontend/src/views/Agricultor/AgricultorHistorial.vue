<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar 
      :brand-name="'CacaoScan'"
      :user-name="userName"
      :user-role="userRole"
      :current-route="route.path"
      :active-section="activeSection"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
      @toggle-collapse="toggleSidebarCollapse"
    />

    <!-- Main Content -->
    <div :class="isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'">
      <main class="py-6 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
          <!-- Header -->
          <div class="mb-8">
            <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <h1 class="text-3xl font-bold text-gray-900">Historial de Análisis</h1>
              <p class="text-gray-600 mt-1">Revisa todos tus análisis de granos de cacao</p>
            </div>
          </div>
        
          <!-- Historial Content -->
          <ImageHistoryCard 
            :initial-images="recentAnalyses"
            :auto-load="true"
            @image-selected="handleImageSelected"
            @refresh-requested="refreshData"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, onMounted } from 'vue'

// 2. Vue router
import { useRoute } from 'vue-router'

// 3. Composables
import { useImageStats } from '@/composables/useImageStats'
import { useSidebarNavigation } from '@/composables/useSidebarNavigation'

// 4. Components
import ImageHistoryCard from '@/components/dashboard/ImageHistoryCard.vue'
import Sidebar from '@/components/layout/Common/Sidebar.vue'

// Route
const route = useRoute()

// Composables
const { fetchImages } = useImageStats()
const {
  isSidebarCollapsed,
  userName,
  userRole,
  handleMenuClick,
  toggleSidebarCollapse,
  handleLogout
} = useSidebarNavigation()

// State
const activeSection = ref('history')
const recentAnalyses = ref([])
const imagesLoading = ref(false)

// Functions
const loadRecentAnalyses = async () => {
  imagesLoading.value = true
  try {
    const data = await fetchImages(1, { page_size: '10' })
    recentAnalyses.value = data.results.map(image => ({
      id: `CAC-${image.id}`,
      status: image.processed ? 'completed' : 'pending',
      statusLabel: image.processed ? 'Completado' : 'Pendiente',
      quality: image.prediction?.quality || 0,
      date: image.created_at,
      predictions: image.prediction ? [image.prediction] : [],
      ...image
    }))
  } catch (error) {
    } finally {
    imagesLoading.value = false
  }
}

const refreshData = () => {
  loadRecentAnalyses()
}

const handleImageSelected = (image) => {
  }

// Lifecycle
onMounted(() => {
  loadRecentAnalyses()
})
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>

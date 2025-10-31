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
import { ref, computed, onMounted } from 'vue'

// 2. Vue router
import { useRoute, useRouter } from 'vue-router'

// 3. Stores
import { useAuthStore } from '@/stores/auth'

// 4. Composables
import { useImageStats } from '@/composables/useImageStats'

// 5. Components
import ImageHistoryCard from '@/components/dashboard/ImageHistoryCard.vue'
import Sidebar from '@/components/layout/Common/Sidebar.vue'

// Router & Route
const router = useRouter()
const route = useRoute()

// Stores
const authStore = useAuthStore()

// Composables
const { fetchImages } = useImageStats()

// State
const isSidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')
const activeSection = ref('history')
const recentAnalyses = ref([])
const imagesLoading = ref(false)

// Computed
const userName = computed(() => {
  return authStore.userFullName || 'Usuario'
})

const userRole = computed(() => {
  const role = authStore.userRole || 'Usuario'
  if (role === 'admin') return 'admin'
  if (role === 'farmer') return 'agricultor'
  return 'agricultor'
})

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
    console.error('Error loading recent analyses:', error)
  } finally {
    imagesLoading.value = false
  }
}

const refreshData = () => {
  loadRecentAnalyses()
}

const handleImageSelected = (image) => {
  console.log('Imagen seleccionada:', image)
}

const handleMenuClick = (item) => {
  if (item.route && item.route !== null) {
    const currentPath = route.path
    if (currentPath !== item.route) {
      router.push(item.route)
    }
  } else {
    const role = authStore.userRole
    if (role === 'farmer' || role === 'Agricultor') {
      router.push({ 
        name: 'AgricultorDashboard',
        query: { section: item.id }
      })
    } else {
      router.push({ 
        name: 'AdminDashboard',
        query: { section: item.id }
      })
    }
  }
}

const toggleSidebarCollapse = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value)
}

const handleLogout = async () => {
  try {
    await authStore.logout()
  } catch (error) {
    console.error('Error during logout:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadRecentAnalyses()
})
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>

<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Sidebar -->
    <Sidebar
      :brand-name="'CacaoScan'"
      :user-name="userName"
      :user-role="userRole"
      :current-route="route.path"
      :active-section="'fincas'"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
      @toggle-collapse="toggleSidebarCollapse"
    />

    <!-- Main Content -->
    <div :class="isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'" class="w-full relative">
      <!-- Page Content -->
      <main class="py-8 px-4 sm:px-6 lg:px-8 min-h-screen bg-white relative z-0">
        <div class="max-w-7xl mx-auto space-y-8">
          <!-- Breadcrumb Navigation -->
          <nav aria-label="breadcrumb" class="mb-4">
            <ol class="flex items-center space-x-2 text-sm text-gray-600">
              <li>
                <router-link to="/fincas" class="hover:text-green-600 transition-colors">Fincas</router-link>
              </li>
              <li class="text-gray-400">/</li>
              <li v-if="finca" class="text-gray-900 font-medium">
                <router-link :to="`/fincas/${fincaId}`" class="hover:text-green-600 transition-colors">
                  {{ finca.nombre || 'Finca' }}
                </router-link>
              </li>
              <li v-else class="text-gray-400">Finca</li>
              <li class="text-gray-400">/</li>
              <li class="text-gray-900 font-medium" aria-current="page">Lotes</li>
            </ol>
          </nav>

          <!-- Header -->
          <LotesHeader 
            :finca-nombre="finca?.nombre || ''"
            :can-create="canCreate"
            @create="openCreateModal"
          />

          <!-- Filtros -->
          <LotesFilters
            v-model:search-query="searchQuery"
            v-model:filters="filters"
            @apply-filters="applyFilters"
            @clear-filters="clearFilters"
          />

          <!-- Lista de lotes -->
          <LoteList
            :lotes="filteredLotes"
            :loading="loading"
            :error="error"
            :can-edit="canEdit"
            :can-create="canCreate"
            @edit="editLote"
            @analyze="analyzeLote"
            @view-details="viewLote"
            @create="openCreateModal"
            @retry="loadLotes"
          />

          <!-- Modal de formulario -->
          <Teleport to="body">
            <CreateLoteModal
              v-if="showModal && finca && fincaId"
              :finca-id="Number(fincaId)"
              :finca-nombre="finca.nombre || 'Finca'"
              @close="closeModal"
              @lote-created="handleLoteCreated"
            />
          </Teleport>

          <!-- Modal de detalle de lote -->
          <Teleport to="body">
            <LoteDetailModal
              v-if="showDetailModal"
              :show="showDetailModal"
              :lote-id="selectedLoteId"
              @close="closeDetailModal"
            />
          </Teleport>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import { useSidebarNavigation } from '@/composables/useSidebarNavigation'
import { usePagination } from '@/composables/usePagination'
import { getLotesByFinca, getFincaById } from '@/services/fincasApi'
import Sidebar from '@/components/layout/Common/Sidebar.vue'
import LotesHeader from '@/components/common/LotesViewComponents/LotesHeader.vue'
import LotesFilters from '@/components/common/LotesViewComponents/LotesFilters.vue'
import LoteList from '@/components/common/LotesViewComponents/LoteList.vue'
import CreateLoteModal from '@/components/admin/AdminAnalisisComponents/CreateLoteModal.vue'
import LoteDetailModal from '@/components/common/LotesViewComponents/LoteDetailModal.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

// Sidebar navigation composable
const {
  isSidebarCollapsed,
  userName,
  userRole,
  handleMenuClick,
  toggleSidebarCollapse,
  handleLogout
} = useSidebarNavigation()

// Reactive data
const finca = ref(null)
const lotes = ref([])
const loading = ref(true)
const error = ref(null)
const showModal = ref(false)
const showDetailModal = ref(false)
const selectedLoteId = ref(null)

// Filters
const filters = reactive({
  estado: '',
  variedad: ''
})
const searchQuery = ref('')

// Pagination
const pagination = usePagination({
  initialPage: 1,
  initialItemsPerPage: 10
})

// Computed
const fincaId = computed(() => {
  const id = route.params.id
  return id ? parseInt(id, 10) : null
})

const canCreate = computed(() => {
  return authStore.userRole === 'admin' || 
         (authStore.userRole === 'farmer' && finca.value?.agricultor === authStore.user?.id)
})

const canEdit = computed(() => {
  return authStore.userRole === 'admin' || 
         (authStore.userRole === 'farmer' && finca.value?.agricultor === authStore.user?.id)
})

const filteredLotes = computed(() => {
  let filtered = lotes.value

  if (searchQuery.value) {
    const search = searchQuery.value.toLowerCase()
    filtered = filtered.filter(lote => {
      const identificador = lote.identificador?.toLowerCase() || ''
      const nombre = lote.nombre?.toLowerCase() || ''
      const variedadNombre = typeof lote.variedad === 'object' 
        ? lote.variedad?.nombre?.toLowerCase() || ''
        : String(lote.variedad || '').toLowerCase()
      return identificador.includes(search) || 
             nombre.includes(search) || 
             variedadNombre.includes(search)
    })
  }

  if (filters.estado) {
    filtered = filtered.filter(lote => {
      const estadoNombre = typeof lote.estado === 'object' 
        ? lote.estado?.nombre?.toLowerCase() || ''
        : String(lote.estado || '').toLowerCase()
      return estadoNombre === filters.estado.toLowerCase()
    })
  }

  if (filters.variedad) {
    filtered = filtered.filter(lote => {
      const variedadNombre = typeof lote.variedad === 'object' 
        ? lote.variedad?.nombre?.toLowerCase() || ''
        : String(lote.variedad || '').toLowerCase()
      return variedadNombre === filters.variedad.toLowerCase()
    })
  }

  return filtered
})

const stats = computed(() => {
  const total = lotes.value.length
  const activos = lotes.value.filter(lote => {
    const estadoNombre = typeof lote.estado === 'object' 
      ? lote.estado?.nombre?.toLowerCase() || ''
      : String(lote.estado || '').toLowerCase()
    return estadoNombre === 'activo'
  }).length
  const cosechados = lotes.value.filter(lote => {
    const estadoNombre = typeof lote.estado === 'object' 
      ? lote.estado?.nombre?.toLowerCase() || ''
      : String(lote.estado || '').toLowerCase()
    return estadoNombre === 'cosechado'
  }).length
  const analisis = lotes.value.filter(lote => (lote.total_analisis || 0) > 0).length
  
  return {
    total,
    activos,
    cosechados,
    analisis
  }
})

// Methods
const loadFinca = async () => {
  try {
    const data = await getFincaById(fincaId.value)
    finca.value = data
  } catch (err) {
    }
}

const loadLotes = async () => {
  try {
    loading.value = true
    error.value = null
    
    const data = await getLotesByFinca(fincaId.value)
    
    if (data && typeof data === 'object') {
      if (data.lotes && Array.isArray(data.lotes)) {
        lotes.value = data.lotes
        if (data.finca && !finca.value) {
          finca.value = data.finca
        }
      } else if (data.results && Array.isArray(data.results)) {
        lotes.value = data.results
      } else if (Array.isArray(data)) {
        lotes.value = data
      } else {
        lotes.value = []
      }
    } else if (Array.isArray(data)) {
      lotes.value = data
    } else {
      lotes.value = []
    }
  } catch (err) {
    const errorMessage = err.response?.data?.error || err.response?.data?.details || err.message || 'Error al cargar los lotes'
    error.value = errorMessage
    
    if (err.response?.status === 403) {
      error.value = 'No tienes permisos para ver los lotes de esta finca'
    } else if (err.response?.status === 404) {
      error.value = 'La finca no existe o no tienes acceso a ella'
    }
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  showModal.value = true
}

const createLote = () => {
  if (fincaId.value) {
    router.push(`/fincas/${fincaId.value}/lotes/new`)
  }
}

const closeModal = () => {
  showModal.value = false
}

const handleLoteCreated = async (newLote) => {
  closeModal()
  // Recargar lotes después de crear uno nuevo
  await loadLotes()
}

const viewLote = (lote) => {
  const loteId = typeof lote === 'object' ? lote.id : lote
  selectedLoteId.value = loteId
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedLoteId.value = null
}

const editLote = (lote) => {
  const loteId = typeof lote === 'object' ? lote.id : lote
  router.push(`/lotes/${loteId}/edit`)
}

const analyzeLote = (lote) => {
  const loteId = typeof lote === 'object' ? lote.id : lote
  router.push(`/analisis?lote=${loteId}`)
}

const applyFilters = () => {
  // Los filtros se aplican automáticamente a través del computed filteredLotes
}

const clearFilters = () => {
  searchQuery.value = ''
  filters.estado = ''
  filters.variedad = ''
  pagination.goToPage(1)
}

const changePage = (page) => {
  if (page >= 1 && page <= pagination.totalPages.value) {
    pagination.goToPage(page)
  }
}

// Debounced search ya está manejado en LotesFilters

// Lifecycle
onMounted(() => {
  loadFinca()
  loadLotes()
})
</script>

<style scoped>
/* Transiciones suaves */
.transition-colors {
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.transition-shadow {
  transition-property: box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* Animación de carga */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>

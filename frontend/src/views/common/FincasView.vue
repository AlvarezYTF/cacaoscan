<template>
  <div class="min-h-screen bg-gray-100">
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
    <div :class="isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'" class="w-full relative">
      <!-- Page Content -->
      <main class="py-8 px-4 sm:px-6 lg:px-8 min-h-screen bg-white relative z-0">
        <div class="max-w-7xl mx-auto space-y-8">
          <!-- Header -->
          <FincasHeader @create="openCreateModal" />

          <!-- Filtros -->
          <FincasFilters
            v-model:search-query="searchQuery"
            v-model:filters="filters"
            @apply-filters="applyFilters"
            @clear-filters="clearFilters"
          />

          <!-- Lista de fincas -->
          <FincaList
            :fincas="Array.isArray(fincas) ? fincas : []"
            :loading="loading"
            :error="error"
            :user-role="userRole"
            @edit="editFinca"
            @view-lotes="viewLotes"
            @view-details="viewFincaDetails"
            @create="openCreateModal"
            @retry="loadFincas"
            @confirm-delete="confirmDelete"
            @confirm-activate="confirmActivate"
          />

          <!-- Modal de formulario -->
          <Teleport to="body">
            <FincaForm
              v-if="showModal"
              :finca="selectedFinca"
              :is-editing="isEditing"
              @close="closeModal"
              @saved="handleFincaSaved"
            />
          </Teleport>

          <!-- Modal de detalles -->
          <Teleport to="body">
            <FincaDetailModal
              :show="showDetailModal"
              :finca="selectedFincaDetail"
              :user-role="userRole"
              @close="closeDetailModal"
              @edit="editFinca"
              @view-lotes="viewLotes"
            />
          </Teleport>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, onMounted, computed } from 'vue'

// 2. Vue router
import { useRoute, useRouter } from 'vue-router'

// 3. Stores
import { useAuthStore } from '@/stores/auth'
import { useFincasStore } from '@/stores/fincas'

// 4. Components
import Sidebar from '@/components/layout/Common/Sidebar.vue'
import FincaForm from '@/components/FincaForm.vue'
import FincasHeader from '@/components/common/FincasViewComponents/FincasHeader.vue'
import FincasFilters from '@/components/common/FincasViewComponents/FincasFilters.vue'
import FincaList from '@/components/common/FincasViewComponents/FincaList.vue'
import FincaDetailModal from '@/components/common/FincasViewComponents/FincaDetailModal.vue'

// 5. Services
import fincasApi from '@/services/fincasApi'

// 6. Libraries
import Swal from 'sweetalert2'

// Router & Route
const router = useRouter()
const route = useRoute()

// Stores
const authStore = useAuthStore()
const fincasStore = useFincasStore()

// Sidebar collapse state
const isSidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')

// Estado reactivo
const searchQuery = ref('')
const filters = ref({
  departamento: '',
  activa: ''
})
const showModal = ref(false)
const selectedFinca = ref(null)
const isEditing = ref(false)
const showDetailModal = ref(false)
const selectedFincaDetail = ref(null)
const activeSection = ref('fincas')

// Computed
const fincas = computed(() => fincasStore.fincas)
const loading = computed(() => fincasStore.loading)
const error = computed(() => fincasStore.error)

const userName = computed(() => {
  return authStore.userFullName || 'Usuario'
})

const userRole = computed(() => {
  const role = authStore.userRole || 'Usuario'
  // Normalize role for sidebar - Backend returns: 'admin', 'analyst', or 'farmer'
  if (role === 'admin') return 'admin'
  if (role === 'farmer') return 'agricultor'
  return 'agricultor' // Default to agricultor
})

// Flag de admin para decidir qué formulario mostrar en creación
const isAdmin = computed(() => {
  return (
    authStore.user?.is_staff === true ||
    authStore.user?.is_superuser === true ||
    authStore.userRole === 'admin'
  )
})

// Métodos
const loadFincas = async () => {
  const params = {}
  
  // Solo agregar parámetros que tengan valores
  if (searchQuery.value && searchQuery.value.trim()) {
    params.search = searchQuery.value.trim()
  }
  
  if (filters.value.departamento && filters.value.departamento.trim()) {
    params.departamento = filters.value.departamento.trim()
  }
  
  if (filters.value.activa && filters.value.activa !== '') {
    params.activa = filters.value.activa
  }
  
  await fincasStore.fetchFincas(params)
}

const applyFilters = () => {
  loadFincas()
}

const clearFilters = () => {
  searchQuery.value = ''
  filters.value = {
    departamento: '',
    activa: ''
  }
  loadFincas()
}

const openCreateModal = () => {
  selectedFinca.value = null
  isEditing.value = false
  showModal.value = true
}

const editFinca = (finca) => {
  selectedFinca.value = finca
  isEditing.value = true
  showModal.value = true
}

const viewFinca = (finca) => {
  router.push(`/fincas/${finca.id}`)
}

const viewFincaDetails = (finca) => {
  selectedFincaDetail.value = finca
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  setTimeout(() => {
    selectedFincaDetail.value = null
  }, 300)
}

const viewLotes = (finca) => {
  router.push(`/fincas/${finca.id}/lotes`)
}

const closeModal = () => {
  showModal.value = false
  selectedFinca.value = null
  isEditing.value = false
}

const handleFincaSaved = () => {
  closeModal()
  // No es necesario llamar loadFincas() ya que el store lo hace automáticamente
}

const confirmDelete = async (finca) => {
  const result = await Swal.fire({
    icon: 'warning',
    title: '¿Desactivar finca?',
    html: "<p>¿Estás seguro de que deseas desactivar la finca <strong>\"" + finca.nombre + "\"</strong>?</p><p class=\"text-sm text-gray-600 mt-2\">La finca ya no aparecerá en tu lista, pero los datos se conservarán. Puedes contactar a un administrador si necesitas reactivarla.</p>",
    showCancelButton: true,
    confirmButtonText: 'Sí, desactivar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#dc2626',
    cancelButtonColor: '#6b7280',
    reverseButtons: true
  })
  
  if (result.isConfirmed) {
    try {
      await fincasStore.remove(finca.id)
      Swal.fire({
        icon: 'success',
        title: 'Finca desactivada',
        text: 'La finca se desactivó correctamente. Ya no aparecerá en tu lista.',
        timer: 3000,
        showConfirmButton: false
      })
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo desactivar la finca. Intenta nuevamente.',
        timer: 4000
      })
    }
  }
}

const confirmActivate = async (finca) => {
  const result = await Swal.fire({
    icon: 'question',
    title: '¿Activar finca?',
    html: "<p>¿Estás seguro de que deseas reactivar la finca <strong>\"" + finca.nombre + "\"</strong>?</p><p class=\"text-sm text-gray-600 mt-2\">La finca volverá a estar disponible para el agricultor.</p>",
    showCancelButton: true,
    confirmButtonText: 'Sí, activar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#16a34a',
    cancelButtonColor: '#6b7280',
    reverseButtons: true
  })
  
  if (result.isConfirmed) {
    try {
      await fincasStore.activate(finca.id)
      Swal.fire({
        icon: 'success',
        title: 'Finca activada',
        text: "La finca \"" + finca.nombre + "\" ha sido reactivada. El agricultor podrá verla nuevamente en su gestión.",
        timer: 3000,
        showConfirmButton: false
      })
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo activar la finca. Intenta nuevamente.',
        timer: 4000
      })
    }
  }
}

// Sidebar and navbar methods
const handleMenuClick = (item) => {
  if (item.route && item.route !== null) {
    // Navigate to external routes
    const currentPath = router.currentRoute.value.path
    if (currentPath !== item.route) {
      router.push(item.route)
    }
  } else {
    // For internal sections without routes, navigate to dashboard with query param
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
    // Error durante logout - silenciar
  }
}

// Lifecycle
onMounted(() => {
  loadFincas()
})
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>

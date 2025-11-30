<template>
  <div class="bg-gray-50 min-h-screen">
    <!-- Sidebar -->
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
    
    <!-- Contenido principal -->
    <div class="p-6 transition-all duration-300" :class="isSidebarCollapsed ? 'sm:ml-20' : 'sm:ml-64'">
      <!-- Page Header -->
      <div class="mb-8">
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
          <div class="flex items-center justify-between flex-wrap gap-4">
            <div class="flex items-center">
              <div class="bg-green-100 p-3 rounded-lg mr-4">
                <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
              </div>
              <div>
                <h1 class="text-3xl font-bold text-gray-900">Gestión de Agricultores</h1>
                <p class="text-gray-600 mt-1">Administra todos los agricultores y fincas del sistema</p>
              </div>
            </div>
            <!-- Acciones principales -->
            <div class="flex items-center space-x-3">
              <button 
                @click="descargarReporteAgricultores"
                type="button"
                class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-all duration-200 font-semibold shadow-md hover:shadow-lg flex items-center gap-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                Reporte Agricultores
              </button>
              <button 
                @click="handleNewFarmer"
                type="button"
                class="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-all duration-200 font-semibold shadow-md hover:shadow-lg flex items-center gap-2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                Nuevo Agricultor
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Contenido principal -->
      <main class="space-y-6">
        <!-- Estadísticas rápidas -->
        <FarmersStatsCards 
          :total-items="totalItems"
          :farmers="farmers"
          :all-fincas="allFincas"
        />

        <!-- Barra de búsqueda -->
        <FarmersSearchBar 
          v-model:search-query="searchQuery"
          :placeholder="searchPlaceholder"
        />

        <!-- Tabla de agricultores -->
        <FarmersTable 
          :filtered-farmers="displayedFarmers"
          :search-query="searchQuery"
          :filters="filters"
          :table-columns="tableColumns"
          :current-page="currentPage"
          :total-pages="totalPages"
          :total-items="totalItems"
          :items-per-page="itemsPerPage"
          @new-farmer="handleNewFarmer"
          @page-change="handlePageChange"
          @view-farmer="handleViewFarmer"
          @edit-farmer="handleEditFarmer"
          @delete-farmer="handleDeleteFarmer"
          @toggle-status="handleToggleStatus"
        />
      </main>
    </div>

    <!-- Modal para crear agricultor -->
    <CreateFarmerModal 
      ref="createFarmerModalRef"
      @farmer-created="handleFarmerCreated"
    />

    <!-- Modal para ver detalles del agricultor -->
    <FarmerDetailModal 
      ref="farmerDetailModalRef"
      :farmer="selectedFarmer"
      @close="selectedFarmer = null"
    />

    <!-- Modal para editar agricultor -->
    <EditFarmerModal 
      ref="editFarmerModalRef"
      :farmer="selectedFarmerForEdit"
      @farmer-updated="handleFarmerUpdated"
      @close="selectedFarmerForEdit = null"
    />
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { usePagination } from '@/composables/usePagination'

// 2. Vue router
import { useRouter, useRoute } from 'vue-router'

// 3. Components
import AdminSidebar from '@/components/layout/Common/Sidebar.vue'
import FarmersStatsCards from '@/components/admin/AdminAgricultorComponents/FarmersStatsCards.vue'
import FarmersSearchBar from '@/components/admin/AdminAgricultorComponents/FarmersSearchBar.vue'
import FarmersTable from '@/components/admin/AdminAgricultorComponents/FarmersTable.vue'
import CreateFarmerModal from '@/components/admin/AdminAgricultorComponents/CreateFarmerModal.vue'
import FarmerDetailModal from '@/components/admin/AdminAgricultorComponents/FarmerDetailModal.vue'
import EditFarmerModal from '@/components/admin/AdminAgricultorComponents/EditFarmerModal.vue'

// 4. Stores
import { useAuthStore } from '@/stores/auth'

// 5. Services
import authApi from '@/services/authApi'
import { getFincas } from '@/services/fincasApi'
import reportsApi from '@/services/reportsApi'

// 6. Utils
import Swal from 'sweetalert2'

// Router y store
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Estado reactivo
const searchQuery = ref('')
const loading = ref(false)
const allFincas = ref([])
const isSidebarCollapsed = ref(false)

// Paginación usando composable
const pagination = usePagination(1, 10)

// Props para AdminSidebar
const brandName = computed(() => 'CacaoScan')

const userName = computed(() => {
  const user = authStore.user
  if (user?.first_name && user?.last_name) {
    return `${user.first_name} ${user.last_name}`
  }
  return user?.username || 'Administrador'
})

const userRole = computed(() => {
  const role = authStore.userRole || 'Usuario'
  // Normalize role for sidebar - Backend returns: 'admin', 'analyst', or 'farmer'
  if (role === 'admin') return 'admin'
  if (role === 'farmer') return 'agricultor'
  return 'admin' // Default to admin
})

const searchPlaceholder = ref('Buscar agricultor por nombre, email o finca...')

const filters = ref({
  region: '',
  status: ''
})

// Datos reales cargados desde backend
const farmers = ref([])

// Configuración de la tabla
const tableColumns = [
  { key: 'farmer', label: 'Agricultor' },
  { key: 'farm', label: 'Finca' },
  { key: 'region', label: 'Región' },
  { key: 'status', label: 'Estado' },
  { key: 'actions', label: 'Acciones', align: 'right' }
]

// Referencias a los modales
const createFarmerModalRef = ref(null)
const farmerDetailModalRef = ref(null)
const editFarmerModalRef = ref(null)
const selectedFarmer = ref(null)
const selectedFarmerForEdit = ref(null)

// Helper functions
const getUserInitials = (user) => {
  const names = user.first_name?.split(' ') || user.username?.split(' ') || []
  return names.length >= 2 
    ? `${names[0].charAt(0)}${names[1].charAt(0)}`.toUpperCase()
    : user.username?.substring(0, 2).toUpperCase() || 'AA'
}

const createFarmerFromUser = (user) => ({
  id: user.id,
  initials: getUserInitials(user),
  name: `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username,
  email: user.email,
  farm: 'Sin finca',
  hectares: '0 hectáreas',
  region: user.region || 'No especificada',
  status: user.is_active ? 'Activo' : 'Inactivo',
  is_active: user.is_active || false,
  isUpdating: false,
  fincas: []
})

const isFarmer = (user) => {
  return user.role === 'farmer' || (!user.is_superuser && !user.is_staff && !user.is_admin)
}

const addUsersToMap = (users, agricultoresMap) => {
  if (!users) return
  
  for (const user of users) {
    if (isFarmer(user)) {
      agricultoresMap.set(user.id, createFarmerFromUser(user))
    }
  }
}

const getAgricultorIdsFromFincas = (fincas) => {
  if (!fincas) return []
  
  return Array.from(new Set(
    fincas
      .map(f => f.agricultor_id || (f.agricultor?.id) || (typeof f.agricultor === 'number' ? f.agricultor : null))
      .filter(Boolean)
  ))
}

const loadUsersFallback = async (fincas, agricultoresMap) => {
  const ids = getAgricultorIdsFromFincas(fincas)
  if (!ids.length) return
  
  try {
    const usersById = await Promise.all(ids.map(id => authApi.getUser(id).catch(() => null)))
    for (const user of usersById) {
      if (user) {
        agricultoresMap.set(user.id, createFarmerFromUser(user))
      }
    }
  } catch (e) {
    console.warn('Fallback getUser por ID falló parcialmente', e)
  }
}

const getAgricultorIdFromFinca = (finca) => {
  return finca.agricultor_id || finca.agricultor?.id || (typeof finca.agricultor === 'number' ? finca.agricultor : null)
}

const updateFarmerWithFinca = (existingFarmer, finca) => {
  if (existingFarmer.fincas.length === 0) {
    existingFarmer.farm = finca.nombre
    existingFarmer.hectares = `${finca.hectareas} hectáreas`
    existingFarmer.region = finca.departamento || existingFarmer.region
    existingFarmer.status = finca.activa ? 'Activo' : 'Inactivo'
  }
  existingFarmer.fincas.push(finca)
}

const updateFarmersWithFincas = (fincas, agricultoresMap) => {
  if (!fincas) return
  
  for (const finca of fincas) {
    const agricultorId = getAgricultorIdFromFinca(finca)
    if (!agricultorId) continue
    
    const existingFarmer = agricultoresMap.get(agricultorId)
    if (existingFarmer) {
      updateFarmerWithFinca(existingFarmer, finca)
    }
  }
}

// Función para cargar agricultores desde el backend
const loadFarmers = async () => {
  loading.value = true
  try {
    const [usersResponse, fincasResponse] = await Promise.all([
      authApi.getUsers({ role: 'farmer' }),
      getFincas({ page_size: 100 })
    ])
    
    const agricultoresMap = new Map()
    
    addUsersToMap(usersResponse.results, agricultoresMap)
    
    if ((!usersResponse?.results?.length) && fincasResponse.results) {
      await loadUsersFallback(fincasResponse.results, agricultoresMap)
    }

    updateFarmersWithFincas(fincasResponse.results, agricultoresMap)
    
    farmers.value = Array.from(agricultoresMap.values())
    allFincas.value = fincasResponse.results || []
  } catch (error) {
    console.error('Error cargando agricultores:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudieron cargar los agricultores',
      confirmButtonColor: '#10b981'
    })
  } finally {
    loading.value = false
  }
}

// Computed properties
const filteredFarmers = computed(() => {
  let filtered = farmers.value
  
  // Filtrar por búsqueda
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(farmer => 
      farmer.name.toLowerCase().includes(query) ||
      farmer.email.toLowerCase().includes(query) ||
      farmer.farm.toLowerCase().includes(query)
    )
  }
  
  // Filtrar por región
  if (filters.value.region) {
    filtered = filtered.filter(farmer => farmer.region === filters.value.region)
  }
  
  // Filtrar por estado
  if (filters.value.status) {
    filtered = filtered.filter(farmer => farmer.status === filters.value.status)
  }
  
  return filtered
})

// Actualizar totalItems en paginación cuando cambian los filteredFarmers
const totalItems = computed(() => filteredFarmers.value.length)

watch(totalItems, (newTotal) => {
  pagination.updatePagination({
    page: pagination.currentPage.value,
    page_size: pagination.itemsPerPage.value,
    count: newTotal
  })
}, { immediate: true })

// Paginación en cliente: elementos mostrados en la página actual
const displayedFarmers = computed(() => {
  const start = (pagination.currentPage.value - 1) * pagination.itemsPerPage.value
  const end = start + pagination.itemsPerPage.value
  return filteredFarmers.value.slice(start, end)
})

// Computed para compatibilidad con el template
const currentPage = computed(() => pagination.currentPage.value)
const totalPages = computed(() => pagination.totalPages.value)
const itemsPerPage = computed(() => pagination.itemsPerPage.value)

// Métodos para AdminSidebar
const handleMenuClick = (menuItem) => {
  if (menuItem.route) {
    router.push(menuItem.route)
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Error al cerrar sesión:', error)
  }
}

const toggleSidebarCollapse = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value)
}

const descargarReporteAgricultores = async () => {
  try {
    Swal.fire({
      title: 'Generando reporte...',
      text: 'Por favor espera mientras se genera el reporte Excel',
      allowOutsideClick: false,
      allowEscapeKey: false,
      showConfirmButton: false,
      didOpen: () => {
        Swal.showLoading()
      }
    })
    
    await reportsApi.downloadReporteAgricultores()
    
    Swal.fire({
      icon: 'success',
      title: 'Reporte generado',
      text: 'El reporte se ha descargado exitosamente',
      timer: 3000,
      showConfirmButton: false
    })
  } catch (error) {
    console.error('Error descargando reporte:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo generar el reporte. Por favor intenta nuevamente.',
      confirmButtonText: 'Aceptar'
    })
  }
}

const handleNewFarmer = async () => {
  await nextTick()
  if (createFarmerModalRef.value && typeof createFarmerModalRef.value.openModal === 'function') {
    createFarmerModalRef.value.openModal()
  }
}

const handleFarmerCreated = async () => {
  await loadFarmers()
  Swal.fire({
    toast: true,
    position: 'top-end',
    icon: 'success',
    title: 'Agricultor creado exitosamente',
    showConfirmButton: false,
    timer: 2000
  })
}

const handleViewFarmer = async (farmer) => {
  selectedFarmer.value = farmer
  await nextTick()
  if (farmerDetailModalRef.value && typeof farmerDetailModalRef.value.openModal === 'function') {
    farmerDetailModalRef.value.openModal()
  }
}

const handleEditFarmer = async (farmer) => {
  selectedFarmerForEdit.value = farmer
  await nextTick()
  if (editFarmerModalRef.value && typeof editFarmerModalRef.value.openModal === 'function') {
    editFarmerModalRef.value.openModal()
  }
}

const handleFarmerUpdated = () => {
  loadFarmers()
}

const handleDeleteFarmer = async (farmer) => {
  try {
    const result = await Swal.fire({
      title: '¿Estás seguro?',
      html: `
        <div class="text-center">
          <svg class="mx-auto text-red-600 w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
          <p class="text-gray-700 mb-2">Se eliminará el agricultor:</p>
          <p class="text-lg font-bold text-gray-900 mb-4">${farmer.name}</p>
          <p class="text-sm text-red-600">Esta acción no se puede deshacer</p>
        </div>
      `,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#6b7280',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar',
      focusCancel: true,
      customClass: {
        popup: 'rounded-xl',
        confirmButton: 'px-6 py-2.5 rounded-lg font-semibold hover:bg-red-700 transition-all duration-200',
        cancelButton: 'px-6 py-2.5 rounded-lg font-semibold hover:bg-gray-200 transition-all duration-200'
      }
    })

    if (result.isConfirmed) {
      Swal.fire({
        title: 'Eliminando...',
        text: 'Por favor espera',
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        didOpen: () => {
          Swal.showLoading()
        }
      })

      await authApi.deleteUser(farmer.id)

      Swal.fire({
        icon: 'success',
        title: '¡Eliminado!',
        text: 'El agricultor ha sido eliminado exitosamente',
        confirmButtonColor: '#10b981',
        timer: 2000
      })

      await loadFarmers()
    }
  } catch (error) {
    console.error('Error eliminando agricultor:', error)
    const errorMessage = error.response?.data?.error || error.response?.data?.message || 'Error al eliminar el agricultor'
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: errorMessage,
      confirmButtonColor: '#ef4444'
    })
  }
}

const handleToggleStatus = async (farmer) => {
  try {
    farmer.isUpdating = true
    const newStatus = !farmer.is_active
    
    await authApi.toggleUserStatus(farmer.id, newStatus)
    
    farmer.is_active = newStatus
    farmer.status = newStatus ? 'Activo' : 'Inactivo'
    
    Swal.fire({
      icon: 'success',
      title: 'Estado actualizado',
      text: `El agricultor ahora está ${newStatus ? 'activo' : 'inactivo'}`,
      confirmButtonColor: '#10b981',
      timer: 2000,
      showConfirmButton: false
    })
  } catch (error) {
    console.error('Error cambiando estado:', error)
    const errorMessage = error.response?.data?.error || error.response?.data?.message || 'Error al cambiar el estado del agricultor'
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: errorMessage,
      confirmButtonColor: '#ef4444'
    })
  } finally {
    farmer.isUpdating = false
  }
}

const handlePageChange = (page) => {
  pagination.goToPage(page)
}

// Lifecycle
onMounted(async () => {
  checkScreenSize()
  globalThis.addEventListener('resize', checkScreenSize)
  await loadFarmers()
})

const checkScreenSize = () => {
  try {
    if (globalThis.innerWidth <= 768) {
      isSidebarCollapsed.value = true
      localStorage.setItem('sidebarCollapsed', 'true')
    } else {
      isSidebarCollapsed.value = false
      localStorage.setItem('sidebarCollapsed', 'false')
    }
  } catch (err) {
    console.warn('Error en checkScreenSize:', err)
  }
}
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
/* Eliminados estilos redundantes que ya están en Tailwind */
</style>

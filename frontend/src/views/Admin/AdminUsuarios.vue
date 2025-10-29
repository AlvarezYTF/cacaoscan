<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar Component -->
    <AdminSidebar :brand-name="brandName" :user-name="userName" :user-role="userRole" :current-route="$route.path"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick" @logout="handleLogout" @toggle-collapse="toggleSidebarCollapse" />

    <!-- Main Content -->
    <div class="p-6 transition-all duration-300" :class="isSidebarCollapsed ? 'sm:ml-20' : 'sm:ml-64'">
      <!-- Page Header -->
      <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-8 mb-8">
        <div class="flex items-center justify-between flex-wrap gap-4">
          <div class="flex items-center">
            <div class="bg-green-100 p-3 rounded-lg mr-4">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
              </svg>
            </div>
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Gestión de Usuarios</h1>
              <p class="text-gray-600 mt-1">Administra todos los usuarios del sistema CacaoScan</p>
            </div>
          </div>
          <button @click="openCreateModal"
            class="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 shadow-md hover:shadow-lg">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            Nuevo Usuario
          </button>
        </div>
      </div>

      <!-- Filtros y Búsqueda -->
      <UsersSearchBar 
        :search-query="searchQuery"
        :role-filter="roleFilter"
        :status-filter="statusFilter"
        :sort-by="sortBy"
        @update:search-query="searchQuery = $event; debouncedSearch()"
        @update:role-filter="roleFilter = $event; applyFilters()"
        @update:status-filter="statusFilter = $event; applyFilters()"
        @update:sort-by="sortBy = $event; applyFilters()"
        @clear-filters="clearFilters"
      />

      <!-- Estadísticas Rápidas -->
      <UsersStatsCards 
        :total-users="totalUsers"
        :active-users="activeUsers"
        :new-users-today="newUsersToday"
        :online-users="onlineUsers"
      />

      <!-- Tabla de Usuarios -->
      <UsersTable 
        :users="users"
        :selected-users="selectedUsers"
        :loading="loading"
        @toggle-select-all="toggleSelectAll"
        @toggle-user-select="handleUserSelect"
        @toggle-status="handleToggleStatus"
        @view-user="viewUser"
        @edit-user="editUser"
        @delete-user="confirmDeleteUser"
        @view-activity="viewUserActivity"
        @export="exportUsers"
      />

      <!-- Paginación -->
      <div v-if="totalPages > 1"
        class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 rounded-b-lg sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
          <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
            Anterior
          </button>
          <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
            Siguiente
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              Mostrando página <span class="font-medium">{{ currentPage }}</span> de <span class="font-medium">{{ totalPages }}</span>
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd"
                    d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                    clip-rule="evenodd"></path>
                </svg>
              </button>

              <button v-for="page in visiblePages" :key="page" @click="changePage(page)"
                :class="page === currentPage ? 'z-10 bg-green-50 border-green-500 text-green-600' : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'"
                class="relative inline-flex items-center px-4 py-2 border text-sm font-medium">
                {{ page }}
              </button>

              <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd"
                    d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                    clip-rule="evenodd"></path>
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>

      <!-- Acciones Masivas -->
      <div v-if="selectedUsers.length > 0"
        class="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-white rounded-xl shadow-lg border border-gray-200 p-6 z-50 backdrop-blur-sm">
        <div class="flex items-center space-x-4">
          <span class="text-sm font-medium text-gray-900">
            {{ selectedUsers.length }} usuario(s) seleccionado(s)
          </span>
          <div class="flex items-center space-x-2">
            <button @click="bulkActivate"
              class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Activar
            </button>
            <button @click="bulkDeactivate"
              class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-amber-600 border border-transparent rounded-lg hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 transition-colors duration-200">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728">
                </path>
              </svg>
              Desactivar
            </button>
            <button @click="bulkDelete"
              class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16">
                </path>
              </svg>
              Eliminar
            </button>
          </div>
        </div>
      </div>

      <!-- Modal de Crear/Editar Usuario -->
      <UserFormModal v-if="showUserModal" :user="editingUser" :mode="modalMode" @close="closeUserModal"
        @saved="handleUserSaved" />

      <!-- Modal de Detalles de Usuario -->
      <UserDetailsModal v-if="showDetailsModal" :user="viewingUser" @close="closeDetailsModal"
        @edit="editUserFromDetails" />

      <!-- Modal de Actividad de Usuario -->
      <UserActivityModal v-if="showActivityModal" :user="activityUser" @close="closeActivityModal" />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import Swal from 'sweetalert2'
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'
import { useConfigStore } from '@/stores/config'
import authApi from '@/services/authApi'
import reportsApi from '@/services/reportsApi'
import { useWebSocket } from '@/composables/useWebSocket'
import AdminSidebar from '@/components/layout/Common/Sidebar.vue'
import UserFormModal from '@/components/admin/AdminUserComponents/UserFormModal.vue'
import UserDetailsModal from '@/components/admin/AdminUserComponents/UserDetailsModal.vue'
import UserActivityModal from '@/components/admin/AdminUserComponents/UserActivityModal.vue'
import UsersStatsCards from '@/components/admin/AdminUserComponents/UsersStatsCards.vue'
import UsersSearchBar from '@/components/admin/AdminUserComponents/UsersSearchBar.vue'
import UsersTable from '@/components/admin/AdminUserComponents/UsersTable.vue'
import LoadingSpinner from '@/components/admin/AdminGeneralComponents/LoadingSpinner.vue'

export default {
  name: 'UserManagement',
  components: {
    AdminSidebar,
    UserFormModal,
    UserDetailsModal,
    UserActivityModal,
    UsersStatsCards,
    UsersSearchBar,
    UsersTable,
    LoadingSpinner
  },
  setup() {
    const router = useRouter()
    const adminStore = useAdminStore()
    const authStore = useAuthStore()
    const configStore = useConfigStore()
    const websocket = useWebSocket()

    // Sidebar properties
    const brandName = computed(() => configStore.brandName)
    const userName = computed(() => {
      const user = authStore.user
      return user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username : 'Usuario'
    })
    const isSidebarCollapsed = ref(false)

    const toggleSidebarCollapse = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value
      localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value)
    }
    const userRole = computed(() => {
      const role = authStore.userRole || 'Usuario'
      // Normalize role for sidebar - Backend returns: 'admin', 'analyst', or 'farmer'
      if (role === 'admin') return 'admin'
      if (role === 'farmer') return 'agricultor'
      return 'admin' // Default to admin
    })

    // Navbar properties
    const navbarTitle = ref('Gestión de Usuarios')
    const navbarSubtitle = ref('Administra todos los usuarios del sistema')
    const searchPlaceholder = ref('Buscar usuarios...')
    const refreshButtonText = ref('Actualizar')

    // Reactive data
    const loading = ref(false)
    const users = ref([])
    const selectedUsers = ref([])
    const selectAll = ref(false)

    // Filters and search
    const searchQuery = ref('')
    const roleFilter = ref('')
    const statusFilter = ref('')
    const sortBy = ref('-date_joined')

    // Pagination
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalUsersCount = ref(0)
    const totalPages = ref(0)

    // Modals
    const showUserModal = ref(false)
    const showDetailsModal = ref(false)
    const showActivityModal = ref(false)
    const modalMode = ref('create') // 'create' or 'edit'
    const editingUser = ref(null)
    const viewingUser = ref(null)
    const activityUser = ref(null)

    // Stats from backend
    const userStats = ref({
      total: 0,
      active: 0,
      online: 0,
      new_today: 0
    })

    // Computed - now using backend stats
    const activeUsers = computed(() => userStats.value.active)
    const totalUsers = computed(() => userStats.value.total)
    const onlineUsers = computed(() => userStats.value.online)
    const newUsersToday = computed(() => userStats.value.new_today)

    const visiblePages = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, start + 4)

      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    // Methods
    const debounce = (func, wait) => {
      let timeout
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout)
          func(...args)
        }
        clearTimeout(timeout)
        timeout = setTimeout(later, wait)
      }
    }

    const loadUserStats = async () => {
      try {
        const stats = await authApi.getUserStats()
        userStats.value = {
          total: stats.total || 0,
          active: stats.active || 0,
          online: stats.online || 0,
          new_today: stats.new_today || 0
        }
      } catch (error) {
        console.error('Error loading user stats:', error)
        // Establecer valores por defecto en caso de error
        userStats.value = {
          total: 0,
          active: 0,
          online: 0,
          new_today: 0
        }
      }
    }

    const loadUsers = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          page_size: pageSize.value,
          search: searchQuery.value,
          role: roleFilter.value,
          status: statusFilter.value,
          ordering: sortBy.value
        }

        const response = await adminStore.getAllUsers(params)
        users.value = response.data.results
        totalUsersCount.value = response.data.count
        totalPages.value = Math.ceil(response.data.count / pageSize.value)

      } catch (error) {
        console.error('Error loading users:', error)
        
        // Si es error de conexión, establecer arrays vacíos
        if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
          users.value = []
          totalUsersCount.value = 0
          totalPages.value = 1
        }
        
        // Solo mostrar error si no es un error de red común
        if (!error.response || error.response.status >= 500) {
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudieron cargar los usuarios. Verifica tu conexión al servidor.',
            timer: 3000
          })
        }
      } finally {
        loading.value = false
      }
    }

    const debouncedSearch = debounce(() => {
      currentPage.value = 1
      loadUsers()
    }, 500)

    const applyFilters = () => {
      currentPage.value = 1
      loadUsers()
    }

    const clearFilters = () => {
      searchQuery.value = ''
      roleFilter.value = ''
      statusFilter.value = ''
      sortBy.value = '-date_joined'
      currentPage.value = 1
      loadUsers()
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadUsers()
      }
    }

    const toggleSelectAll = (value) => {
      if (value) {
        selectedUsers.value = users.value.map(user => user.id)
      } else {
        selectedUsers.value = []
      }
    }

    const handleUserSelect = (userId) => {
      const index = selectedUsers.value.indexOf(userId)
      if (index > -1) {
        selectedUsers.value.splice(index, 1)
      } else {
        selectedUsers.value.push(userId)
      }
    }

    const openCreateModal = () => {
      editingUser.value = null
      modalMode.value = 'create'
      showUserModal.value = true
    }

    const editUser = (user) => {
      editingUser.value = user
      modalMode.value = 'edit'
      showUserModal.value = true
    }

    const viewUser = (user) => {
      viewingUser.value = user
      showDetailsModal.value = true
    }

    const viewUserActivity = (user) => {
      activityUser.value = user
      showActivityModal.value = true
    }

    const closeUserModal = () => {
      showUserModal.value = false
      editingUser.value = null
    }

    const closeDetailsModal = () => {
      showDetailsModal.value = false
      viewingUser.value = null
    }

    const closeActivityModal = () => {
      showActivityModal.value = false
      activityUser.value = null
    }

    const editUserFromDetails = (user) => {
      closeDetailsModal()
      editUser(user)
    }

    const handleUserSaved = () => {
      closeUserModal()
      loadUsers()
    }

    const confirmDeleteUser = async (user) => {
      if (user.is_superuser) {
        Swal.fire({
          icon: 'warning',
          title: 'No permitido',
          text: 'No se puede eliminar un superusuario'
        })
        return
      }

      const result = await Swal.fire({
        title: '¿Eliminar usuario?',
        text: `¿Estás seguro de que quieres eliminar a ${user.first_name} ${user.last_name}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      })

      if (result.isConfirmed) {
        await deleteUser(user.id)
      }
    }

    const deleteUser = async (userId) => {
      try {
        await adminStore.deleteUser(userId)

        // Remove from local state
        users.value = users.value.filter(user => user.id !== userId)
        selectedUsers.value = selectedUsers.value.filter(id => id !== userId)
        totalUsersCount.value--

        Swal.fire({
          icon: 'success',
          title: 'Usuario eliminado',
          text: 'El usuario ha sido eliminado exitosamente'
        })

      } catch (error) {
        console.error('Error deleting user:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo eliminar el usuario'
        })
      }
    }

    const bulkActivate = async () => {
      try {
        const promises = selectedUsers.value.map(userId =>
          adminStore.updateUser(userId, { is_active: true })
        )

        await Promise.all(promises)

        // Update local state
        users.value.forEach(user => {
          if (selectedUsers.value.includes(user.id)) {
            user.is_active = true
          }
        })

        selectedUsers.value = []
        selectAll.value = false

        Swal.fire({
          icon: 'success',
          title: 'Usuarios activados',
          text: 'Los usuarios seleccionados han sido activados'
        })

      } catch (error) {
        console.error('Error bulk activating users:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron activar los usuarios'
        })
      }
    }

    const bulkDeactivate = async () => {
      try {
        const promises = selectedUsers.value.map(userId =>
          adminStore.updateUser(userId, { is_active: false })
        )

        await Promise.all(promises)

        // Update local state
        users.value.forEach(user => {
          if (selectedUsers.value.includes(user.id)) {
            user.is_active = false
          }
        })

        selectedUsers.value = []
        selectAll.value = false

        Swal.fire({
          icon: 'success',
          title: 'Usuarios desactivados',
          text: 'Los usuarios seleccionados han sido desactivados'
        })

      } catch (error) {
        console.error('Error bulk deactivating users:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron desactivar los usuarios'
        })
      }
    }

    const bulkDelete = async () => {
      const result = await Swal.fire({
        title: '¿Eliminar usuarios?',
        text: `¿Estás seguro de que quieres eliminar ${selectedUsers.value.length} usuarios?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      })

      if (result.isConfirmed) {
        try {
          const promises = selectedUsers.value.map(userId =>
            adminStore.deleteUser(userId)
          )

          await Promise.all(promises)

          // Remove from local state
          users.value = users.value.filter(user =>
            !selectedUsers.value.includes(user.id)
          )

          totalUsersCount.value -= selectedUsers.value.length
          selectedUsers.value = []
          selectAll.value = false

          Swal.fire({
            icon: 'success',
            title: 'Usuarios eliminados',
            text: 'Los usuarios seleccionados han sido eliminados'
          })

        } catch (error) {
          console.error('Error bulk deleting users:', error)
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudieron eliminar algunos usuarios'
          })
        }
      }
    }

    const handleToggleStatus = async (user) => {
      console.log('Toggle status for user:', user);
      
      try {
        // Marcar el usuario como actualizándose
        user.isUpdating = true;
        
        // Cambiar el estado
        const newStatus = !user.is_active;
        
        // Actualizar en el backend
        await authApi.toggleUserStatus(user.id, newStatus);
        
        // Actualizar estado local sin recargar
        user.is_active = newStatus;
        
        console.log(`✅ Estado actualizado para usuario ${user.username}: ${newStatus ? 'Activo' : 'Inactivo'}`);
        
        // Mostrar notificación de éxito
        Swal.fire({
          icon: 'success',
          title: 'Estado actualizado',
          text: `El usuario ahora está ${newStatus ? 'activo' : 'inactivo'}`,
          confirmButtonColor: '#10b981',
          timer: 2000,
          showConfirmButton: false
        });
        
      } catch (error) {
        console.error('Error cambiando estado:', error);
        
        // Mostrar error
        const errorMessage = error.response?.data?.error || error.response?.data?.message || 'Error al cambiar el estado del usuario';
        
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: errorMessage,
          confirmButtonColor: '#ef4444'
        });
      } finally {
        // Remover el estado de actualización
        user.isUpdating = false;
      }
    };

    const exportUsers = async () => {
      try {
        // Mostrar loading
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
        
        // Usar el nuevo servicio de reportes
        await reportsApi.downloadReporteUsuarios()
        
        // Mostrar éxito
        Swal.fire({
          icon: 'success',
          title: 'Exportación exitosa',
          text: 'Los usuarios han sido exportados exitosamente',
          timer: 3000,
          showConfirmButton: false
        })

      } catch (error) {
        console.error('Error exporting users:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo exportar la lista de usuarios'
        })
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
        'Administrador': 'bg-green-100 text-green-800',
        'Agricultor': 'bg-green-100 text-green-800',
        'Técnico': 'bg-green-100 text-green-800'
      }
      return classes[role] || 'bg-gray-100 text-gray-800'
    }

    const getUserStatusClass = (user) => {
      if (!user.is_active) return 'inactive'
      if (user.last_login) {
        const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000)
        if (new Date(user.last_login) > fiveMinutesAgo) {
          return 'online'
        }
      }
      return 'active'
    }

    // Sidebar event handlers
    const handleMenuClick = (menuItem) => {
      console.log('Menu clicked:', menuItem)
      router.push(menuItem.route)
    }

    const handleLogout = async () => {
      const result = await Swal.fire({
        title: '¿Cerrar sesión?',
        text: '¿Estás seguro de que quieres cerrar sesión?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, cerrar sesión',
        cancelButtonText: 'Cancelar'
      })

      if (result.isConfirmed) {
        await authStore.logout()
        router.push('/login')
      }
    }

    // Navbar event handlers
    const handleSearch = (query) => {
      searchQuery.value = query
      debouncedSearch()
    }

    const handleRefresh = () => {
      loadUsers()
    }

    // Watchers
    watch(selectedUsers, (newValue) => {
      selectAll.value = newValue.length === users.value.length && users.value.length > 0
    })

    // Lifecycle
    onMounted(() => {
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

      loadUserStats()
      loadUsers()
      
      // Conectar a WebSocket para estadísticas en tiempo real
      setupWebSocketConnection()
      
      // Configurar polling para actualizaciones periódicas (fallback si WebSockets fallan)
      const statsPollingInterval = setInterval(() => {
        loadUserStats()
        // Solo recargar usuarios si están en la primera página
        if (currentPage.value === 1) {
          loadUsers()
        }
      }, 30000) // Actualizar cada 30 segundos
      
      // Limpiar intervalo y listeners de WebSocket al desmontar
      onUnmounted(() => {
        clearInterval(statsPollingInterval)
        // Limpiar listeners de WebSocket si es necesario
        if (websocket && websocket.off) {
          websocket.off('user-stats-updated', handleStatsUpdate)
        }
      })
    })
    

    
    const setupWebSocketConnection = () => {
      // Escuchar actualizaciones de estadísticas
      websocket.on('user-stats-updated', handleStatsUpdate)
    }
    
    const handleStatsUpdate = (data) => {
      console.log('📊 Actualización de estadísticas recibida:', data)
      userStats.value = {
        total: data.total || 0,
        active: data.active || 0,
        online: data.online || 0,
        new_today: data.new_today || 0
      }
    }

    return {
      // Sidebar & Navbar
      isSidebarCollapsed,
      toggleSidebarCollapse,
      brandName,
      userName,
      userRole,
      navbarTitle,
      navbarSubtitle,
      searchPlaceholder,
      refreshButtonText,

      // Data
      loading,
      users,
      selectedUsers,
      selectAll,
      searchQuery,
      roleFilter,
      statusFilter,
      sortBy,
      currentPage,
      totalUsers,
      totalPages,
      showUserModal,
      showDetailsModal,
      showActivityModal,
      modalMode,
      editingUser,
      viewingUser,
      activityUser,

      // Computed
      activeUsers,
      newUsersToday,
      onlineUsers,
      visiblePages,

      // Methods
      loadUserStats,
      loadUsers,
      debouncedSearch,
      applyFilters,
      clearFilters,
      changePage,
      toggleSelectAll,
      handleUserSelect,
      openCreateModal,
      editUser,
      viewUser,
      viewUserActivity,
      closeUserModal,
      closeDetailsModal,
      closeActivityModal,
      editUserFromDetails,
      handleUserSaved,
      confirmDeleteUser,
      bulkActivate,
      bulkDeactivate,
      bulkDelete,
      handleToggleStatus,
      exportUsers,
      formatDate,
      formatDateTime,
      getRoleBadgeClass,
      getUserStatusClass,
      handleMenuClick,
      handleLogout,
      handleSearch,
      handleRefresh
    }
  }
}
</script>

<style scoped>
/* Estilos específicos para UserManagement */
.user-management {
  padding: 0;
  background-color: transparent;
  min-height: auto;
}

/* Transiciones suaves */
.transition-colors {
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Mejoras de accesibilidad */
button:focus-visible {
  outline: 2px solid rgb(34 197 94);
  outline-offset: 2px;
}

input:focus-visible {
  outline: 2px solid rgb(34 197 94);
  outline-offset: 2px;
}

select:focus-visible {
  outline: 2px solid rgb(34 197 94);
  outline-offset: 2px;
}

/* Estilos para elementos de estado */
.text-green-600 {
  color: rgb(34 197 94);
}

.text-green-700 {
  color: rgb(21 128 61);
}

.text-green-800 {
  color: rgb(22 101 52);
}

.bg-green-50 {
  background-color: rgb(240 253 244);
}

.bg-green-100 {
  background-color: rgb(220 252 231);
}

.border-green-200 {
  border-color: rgb(187 247 208);
}

.border-green-500 {
  border-color: rgb(34 197 94);
}

.hover\:border-green-200:hover {
  border-color: rgb(187 247 208);
}

.hover\:text-green-700:hover {
  color: rgb(21 128 61);
}

.hover\:bg-green-50:hover {
  background-color: rgb(240 253 244);
}

.focus\:ring-green-500:focus {
  --tw-ring-color: rgb(34 197 94);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .grid-cols-1 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }

  .md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }

  .lg\:grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}
</style>

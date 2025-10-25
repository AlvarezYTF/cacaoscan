<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar Component -->
    <AdminSidebar 
      :brand-name="brandName"
      :user-name="userName"
      :user-role="userRole"
      :current-route="$route.path"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
    />

    <!-- Navbar Component -->
    <AdminNavbar 
      :title="navbarTitle"
      :subtitle="navbarSubtitle"
      :user-name="userName"
      :user-role="userRole"
      :search-placeholder="searchPlaceholder"
      :refresh-button-text="refreshButtonText"
      :loading="loading"
      :initial-search-query="searchQuery"
      @search="handleSearch"
      @refresh="handleRefresh"
    />

    <!-- Main Content -->
    <div class="p-4 sm:ml-64">
      <div class="user-management">
        <!-- Header -->
        <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="fas fa-users-cog"></i>
          Gestión de Usuarios
        </h1>
        <div class="header-actions">
          <button 
            class="btn btn-primary"
            @click="openCreateModal"
          >
            <i class="fas fa-plus"></i>
            Nuevo Usuario
          </button>
        </div>
      </div>
    </div>

    <!-- Filtros y Búsqueda -->
    <div class="filters-section">
      <div class="filters-row">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="Buscar usuarios..."
            @input="debouncedSearch"
          >
        </div>
        
        <div class="filter-group">
          <select v-model="roleFilter" @change="applyFilters">
            <option value="">Todos los roles</option>
            <option value="Administrador">Administrador</option>
            <option value="Agricultor">Agricultor</option>
            <option value="Técnico">Técnico</option>
          </select>
        </div>

        <div class="filter-group">
          <select v-model="statusFilter" @change="applyFilters">
            <option value="">Todos los estados</option>
            <option value="active">Activos</option>
            <option value="inactive">Inactivos</option>
          </select>
        </div>

        <div class="filter-group">
          <select v-model="sortBy" @change="applyFilters">
            <option value="-date_joined">Más recientes</option>
            <option value="date_joined">Más antiguos</option>
            <option value="username">Nombre de usuario</option>
            <option value="email">Email</option>
            <option value="last_login">Último login</option>
          </select>
        </div>

        <button 
          class="btn btn-outline-secondary"
          @click="clearFilters"
        >
          <i class="fas fa-times"></i>
          Limpiar
        </button>
      </div>
    </div>

    <!-- Estadísticas Rápidas -->
    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-number">{{ totalUsers }}</div>
        <div class="stat-label">Total Usuarios</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ activeUsers }}</div>
        <div class="stat-label">Activos</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ newUsersToday }}</div>
        <div class="stat-label">Nuevos Hoy</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ onlineUsers }}</div>
        <div class="stat-label">En Línea</div>
      </div>
    </div>

    <!-- Tabla de Usuarios -->
    <div class="table-container">
      <div class="table-header">
        <h3>Lista de Usuarios</h3>
        <div class="table-actions">
          <button 
            class="btn btn-sm btn-outline-primary"
            @click="exportUsers"
            :disabled="loading"
          >
            <i class="fas fa-download"></i>
            Exportar
          </button>
        </div>
      </div>

      <div class="table-body">
        <div v-if="loading" class="loading-state">
          <LoadingSpinner size="lg" color="blue" />
          <p>Cargando usuarios...</p>
        </div>

        <div v-else-if="users.length === 0" class="empty-state">
          <i class="fas fa-users"></i>
          <h3>No se encontraron usuarios</h3>
          <p>No hay usuarios que coincidan con los filtros aplicados.</p>
        </div>

        <table v-else class="table">
          <thead>
            <tr>
              <th>
                <input 
                  type="checkbox" 
                  v-model="selectAll"
                  @change="toggleSelectAll"
                >
              </th>
              <th>Usuario</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Último Login</th>
              <th>Registro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id" :class="{ selected: selectedUsers.includes(user.id) }">
              <td>
                <input 
                  type="checkbox" 
                  :value="user.id"
                  v-model="selectedUsers"
                >
              </td>
              <td>
                <div class="user-info">
                  <div class="user-avatar" :class="getUserStatusClass(user)">
                    <i class="fas fa-user"></i>
                  </div>
                  <div class="user-details">
                    <strong>{{ user.first_name }} {{ user.last_name }}</strong>
                    <small>@{{ user.username }}</small>
                  </div>
                </div>
              </td>
              <td>{{ user.email }}</td>
              <td>
                <span class="badge" :class="getRoleBadgeClass(user.role)">
                  {{ user.role || 'Sin rol' }}
                </span>
              </td>
              <td>
                <span class="badge" :class="user.is_active ? 'badge-success' : 'badge-danger'">
                  {{ user.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td>
                <span v-if="user.last_login" class="last-login">
                  {{ formatDateTime(user.last_login) }}
                </span>
                <span v-else class="text-muted">Nunca</span>
              </td>
              <td>{{ formatDate(user.date_joined) }}</td>
              <td>
                <div class="action-buttons">
                  <button 
                    class="btn btn-sm btn-outline-primary"
                    @click="viewUser(user)"
                    title="Ver detalles"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-warning"
                    @click="editUser(user)"
                    title="Editar"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-info"
                    @click="viewUserActivity(user)"
                    title="Ver actividad"
                  >
                    <i class="fas fa-history"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="confirmDeleteUser(user)"
                    title="Eliminar"
                    :disabled="user.is_superuser"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginación -->
      <div v-if="totalPages > 1" class="pagination-container">
        <nav aria-label="Paginación de usuarios">
          <ul class="pagination">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button 
                class="page-link"
                @click="changePage(currentPage - 1)"
                :disabled="currentPage === 1"
              >
                <i class="fas fa-chevron-left"></i>
              </button>
            </li>
            
            <li 
              v-for="page in visiblePages" 
              :key="page"
              class="page-item"
              :class="{ active: page === currentPage }"
            >
              <button 
                class="page-link"
                @click="changePage(page)"
              >
                {{ page }}
              </button>
            </li>
            
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button 
                class="page-link"
                @click="changePage(currentPage + 1)"
                :disabled="currentPage === totalPages"
              >
                <i class="fas fa-chevron-right"></i>
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Acciones Masivas -->
    <div v-if="selectedUsers.length > 0" class="bulk-actions">
      <div class="bulk-actions-content">
        <span class="selected-count">
          {{ selectedUsers.length }} usuario(s) seleccionado(s)
        </span>
        <div class="bulk-buttons">
          <button 
            class="btn btn-sm btn-success"
            @click="bulkActivate"
          >
            <i class="fas fa-check"></i>
            Activar
          </button>
          <button 
            class="btn btn-sm btn-warning"
            @click="bulkDeactivate"
          >
            <i class="fas fa-ban"></i>
            Desactivar
          </button>
          <button 
            class="btn btn-sm btn-danger"
            @click="bulkDelete"
          >
            <i class="fas fa-trash"></i>
            Eliminar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Crear/Editar Usuario -->
    <UserFormModal
      v-if="showUserModal"
      :user="editingUser"
      :mode="modalMode"
      @close="closeUserModal"
      @saved="handleUserSaved"
    />

    <!-- Modal de Detalles de Usuario -->
    <UserDetailsModal
      v-if="showDetailsModal"
      :user="viewingUser"
      @close="closeDetailsModal"
      @edit="editUserFromDetails"
    />

    <!-- Modal de Actividad de Usuario -->
    <UserActivityModal
      v-if="showActivityModal"
      :user="activityUser"
      @close="closeActivityModal"
    />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import Swal from 'sweetalert2'
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'
import AdminSidebar from '@/components/layout/AdminSidebar.vue'
import AdminNavbar from '@/components/layout/AdminNavbar.vue'
import UserFormModal from '@/components/admin/UserFormModal.vue'
import UserDetailsModal from '@/components/admin/UserDetailsModal.vue'
import UserActivityModal from '@/components/admin/UserActivityModal.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

export default {
  name: 'UserManagement',
  components: {
    AdminSidebar,
    AdminNavbar,
    UserFormModal,
    UserDetailsModal,
    UserActivityModal,
    LoadingSpinner
  },
  setup() {
    const router = useRouter()
    const adminStore = useAdminStore()
    const authStore = useAuthStore()

    // Sidebar properties
    const brandName = computed(() => 'CacaoScan')
    const userName = computed(() => {
      const user = authStore.user
      return user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username : 'Usuario'
    })
    const userRole = computed(() => {
      const user = authStore.user
      if (user?.is_superuser) return 'Superadministrador'
      if (user?.is_staff) return 'Administrador'
      return 'Usuario'
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
    const totalUsers = ref(0)
    const totalPages = ref(0)
    
    // Modals
    const showUserModal = ref(false)
    const showDetailsModal = ref(false)
    const showActivityModal = ref(false)
    const modalMode = ref('create') // 'create' or 'edit'
    const editingUser = ref(null)
    const viewingUser = ref(null)
    const activityUser = ref(null)

    // Computed
    const activeUsers = computed(() => 
      users.value.filter(user => user.is_active).length
    )
    
    const newUsersToday = computed(() => {
      const today = new Date().toDateString()
      return users.value.filter(user => 
        new Date(user.date_joined).toDateString() === today
      ).length
    })
    
    const onlineUsers = computed(() => {
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000)
      return users.value.filter(user => 
        user.last_login && new Date(user.last_login) > fiveMinutesAgo
      ).length
    })
    
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
        totalUsers.value = response.data.count
        totalPages.value = Math.ceil(response.data.count / pageSize.value)
        
      } catch (error) {
        console.error('Error loading users:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron cargar los usuarios'
        })
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

    const toggleSelectAll = () => {
      if (selectAll.value) {
        selectedUsers.value = users.value.map(user => user.id)
      } else {
        selectedUsers.value = []
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
        totalUsers.value--
        
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
          
          totalUsers.value -= selectedUsers.value.length
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

    const exportUsers = async () => {
      try {
        const response = await adminStore.exportData('users', 'excel', {
          search: searchQuery.value,
          role: roleFilter.value,
          status: statusFilter.value
        })
        
        // Create download link
        const blob = new Blob([response.data], { 
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
        })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `usuarios_${new Date().toISOString().split('T')[0]}.xlsx`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        Swal.fire({
          icon: 'success',
          title: 'Exportación exitosa',
          text: 'Los usuarios han sido exportados exitosamente'
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
        'Administrador': 'badge-danger',
        'Agricultor': 'badge-success',
        'Técnico': 'badge-info'
      }
      return classes[role] || 'badge-secondary'
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

      loadUsers()
    })

    return {
      // Sidebar & Navbar
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
      loadUsers,
      debouncedSearch,
      applyFilters,
      clearFilters,
      changePage,
      toggleSelectAll,
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
.user-management {
  padding: 0;
  background-color: transparent;
  min-height: auto;
}

.page-header {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0;
  color: #2c3e50;
  font-size: 1.8rem;
}

.page-title i {
  margin-right: 10px;
  color: #3498db;
}

.filters-section {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filters-row {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #7f8c8d;
}

.search-box input {
  width: 100%;
  padding: 10px 10px 10px 35px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
}

.filter-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  min-width: 150px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  background: white;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.table-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.table-header {
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-header h3 {
  margin: 0;
  color: #2c3e50;
}

.table-body {
  padding: 0;
}

.loading-state,
.empty-state {
  padding: 40px;
  text-align: center;
  color: #7f8c8d;
}

.loading-state i {
  font-size: 2rem;
  margin-bottom: 10px;
  color: #3498db;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 15px;
  color: #bdc3c7;
}

.table {
  margin: 0;
  width: 100%;
}

.table th {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  font-weight: 600;
  color: #495057;
  padding: 15px;
}

.table td {
  padding: 15px;
  border-bottom: 1px solid #dee2e6;
}

.table tbody tr:hover {
  background-color: #f8f9fa;
}

.table tbody tr.selected {
  background-color: #e3f2fd;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  position: relative;
}

.user-avatar.online::after {
  content: '';
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background-color: #27ae60;
  border-radius: 50%;
  border: 2px solid white;
}

.user-avatar.inactive {
  background-color: #95a5a6;
}

.user-details strong {
  display: block;
  color: #2c3e50;
  font-size: 0.9rem;
}

.user-details small {
  color: #7f8c8d;
  font-size: 0.8rem;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.badge-success {
  background-color: #d4edda;
  color: #155724;
}

.badge-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.badge-warning {
  background-color: #fff3cd;
  color: #856404;
}

.badge-info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.badge-secondary {
  background-color: #e2e3e5;
  color: #383d41;
}

.last-login {
  font-size: 0.8rem;
  color: #495057;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.action-buttons .btn {
  padding: 5px 8px;
  font-size: 0.8rem;
}

.pagination-container {
  padding: 20px;
  display: flex;
  justify-content: center;
}

.pagination {
  margin: 0;
}

.page-item.active .page-link {
  background-color: #3498db;
  border-color: #3498db;
}

.page-link {
  color: #3498db;
  border-color: #dee2e6;
}

.page-link:hover {
  color: #2980b9;
  background-color: #e9ecef;
  border-color: #dee2e6;
}

.bulk-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 10px;
  padding: 15px 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
}

.bulk-actions-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.selected-count {
  font-weight: 500;
  color: #2c3e50;
}

.bulk-buttons {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>

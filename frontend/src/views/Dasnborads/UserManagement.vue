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
    <div class="p-6 sm:ml-64">
      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 mb-2">Gestión de Usuarios</h1>
            <p class="text-gray-600 text-lg">Administra todos los usuarios del sistema CacaoScan</p>
          </div>
          <div class="flex items-center space-x-3">
          <button 
            @click="openCreateModal"
              class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
          >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
            Nuevo Usuario
          </button>
        </div>
      </div>
    </div>

    <!-- Filtros y Búsqueda -->
      <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div class="flex flex-col lg:flex-row gap-4 items-start lg:items-center">
          <div class="flex-1 min-w-0">
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </div>
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="Buscar usuarios..."
            @input="debouncedSearch"
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-green-500 focus:border-green-500 text-sm"
          >
            </div>
        </div>
        
          <div class="flex flex-wrap gap-3">
            <select 
              v-model="roleFilter" 
              @change="applyFilters"
              class="block w-full lg:w-auto px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            >
            <option value="">Todos los roles</option>
            <option value="Administrador">Administrador</option>
            <option value="Agricultor">Agricultor</option>
            <option value="Técnico">Técnico</option>
          </select>

            <select 
              v-model="statusFilter" 
              @change="applyFilters"
              class="block w-full lg:w-auto px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            >
            <option value="">Todos los estados</option>
            <option value="active">Activos</option>
            <option value="inactive">Inactivos</option>
          </select>

            <select 
              v-model="sortBy" 
              @change="applyFilters"
              class="block w-full lg:w-auto px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            >
            <option value="-date_joined">Más recientes</option>
            <option value="date_joined">Más antiguos</option>
            <option value="username">Nombre de usuario</option>
            <option value="email">Email</option>
            <option value="last_login">Último login</option>
          </select>

        <button 
          @click="clearFilters"
              class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
        >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
          Limpiar
        </button>
          </div>
      </div>
    </div>

    <!-- Estadísticas Rápidas -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md hover:border-green-200 transition-all duration-200">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-gray-50">
              <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
              </svg>
      </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Total Usuarios</p>
              <p class="text-2xl font-bold text-gray-900">{{ totalUsers }}</p>
      </div>
      </div>
        </div>
        
        <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md hover:border-green-200 transition-all duration-200">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-green-50">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Activos</p>
              <p class="text-2xl font-bold text-gray-900">{{ activeUsers }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md hover:border-green-200 transition-all duration-200">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-blue-50">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Nuevos Hoy</p>
              <p class="text-2xl font-bold text-gray-900">{{ newUsersToday }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md hover:border-green-200 transition-all duration-200">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-green-50">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">En Línea</p>
              <p class="text-2xl font-bold text-gray-900">{{ onlineUsers }}</p>
            </div>
          </div>
      </div>
    </div>

    <!-- Tabla de Usuarios -->
      <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900">Lista de Usuarios</h3>
          <div class="flex items-center space-x-3">
          <button 
            @click="exportUsers"
            :disabled="loading"
              class="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            Exportar
          </button>
        </div>
      </div>

      <div class="table-body">
        <div v-if="loading" class="flex flex-col items-center justify-center py-12">
          <LoadingSpinner size="lg" color="green" />
          <p class="mt-4 text-gray-600">Cargando usuarios...</p>
        </div>

        <div v-else-if="users.length === 0" class="flex flex-col items-center justify-center py-12">
          <svg class="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-2">No se encontraron usuarios</h3>
          <p class="text-gray-600 text-center">No hay usuarios que coincidan con los filtros aplicados.</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
            <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <input 
                  type="checkbox" 
                  v-model="selectAll"
                  @change="toggleSelectAll"
                    class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                >
              </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rol</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Último Login</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Registro</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="user in users" :key="user.id" :class="{ 'bg-green-50': selectedUsers.includes(user.id) }" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                <input 
                  type="checkbox" 
                  :value="user.id"
                  v-model="selectedUsers"
                    class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                >
              </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                      <div class="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
                        <svg class="h-5 w-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                        </svg>
                  </div>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">
                        {{ user.first_name }} {{ user.last_name }}
                      </div>
                      <div class="text-sm text-gray-500">@{{ user.username }}</div>
                  </div>
                </div>
              </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ user.email }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getRoleBadgeClass(user.role)">
                  {{ user.role || 'Sin rol' }}
                </span>
              </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                  {{ user.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span v-if="user.last_login">{{ formatDateTime(user.last_login) }}</span>
                  <span v-else class="text-gray-400">Nunca</span>
              </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(user.date_joined) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex items-center space-x-2">
                  <button 
                    @click="viewUser(user)"
                      class="text-green-600 hover:text-green-700 p-2 rounded-lg hover:bg-green-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500"
                    title="Ver detalles"
                  >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                      </svg>
                  </button>
                  <button 
                    @click="editUser(user)"
                      class="text-amber-600 hover:text-amber-700 p-2 rounded-lg hover:bg-amber-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-amber-500"
                    title="Editar"
                  >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                      </svg>
                  </button>
                  <button 
                    @click="viewUserActivity(user)"
                      class="text-blue-600 hover:text-blue-700 p-2 rounded-lg hover:bg-blue-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    title="Ver actividad"
                  >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                  </button>
                  <button 
                    @click="confirmDeleteUser(user)"
                      class="text-red-600 hover:text-red-700 p-2 rounded-lg hover:bg-red-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Eliminar"
                    :disabled="user.is_superuser"
                  >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>

      <!-- Paginación -->
        <div v-if="totalPages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div class="flex-1 flex justify-between sm:hidden">
              <button 
                @click="changePage(currentPage - 1)"
                :disabled="currentPage === 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
              Anterior
              </button>
            <button 
              @click="changePage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
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
                <button 
                  @click="changePage(currentPage - 1)"
                  :disabled="currentPage === 1"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                  </svg>
                </button>
                
                <button 
              v-for="page in visiblePages" 
              :key="page"
                @click="changePage(page)"
                  :class="page === currentPage ? 'z-10 bg-green-50 border-green-500 text-green-600' : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'"
                  class="relative inline-flex items-center px-4 py-2 border text-sm font-medium"
              >
                {{ page }}
              </button>
            
              <button 
                @click="changePage(currentPage + 1)"
                :disabled="currentPage === totalPages"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                  <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                  </svg>
              </button>
        </nav>
            </div>
          </div>
      </div>
    </div>

    <!-- Acciones Masivas -->
      <div v-if="selectedUsers.length > 0" class="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-white rounded-lg border border-gray-200 shadow-lg p-4 z-50">
        <div class="flex items-center space-x-4">
          <span class="text-sm font-medium text-gray-900">
          {{ selectedUsers.length }} usuario(s) seleccionado(s)
        </span>
          <div class="flex items-center space-x-2">
          <button 
            @click="bulkActivate"
              class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
          >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            Activar
          </button>
          <button 
            @click="bulkDeactivate"
              class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-amber-600 border border-transparent rounded-lg hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 transition-colors duration-200"
          >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"></path>
              </svg>
            Desactivar
          </button>
          <button 
            @click="bulkDelete"
              class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200"
          >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
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

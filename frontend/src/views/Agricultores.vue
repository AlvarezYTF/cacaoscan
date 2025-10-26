<template>
  <div class="bg-gray-50 min-h-screen">
    <!-- Sidebar -->
    <AdminSidebar 
      :brand-name="brandName"
      :user-name="userName"
      :user-role="userRole"
      :current-route="$route.path"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
    />
    
    <!-- Navbar -->
    <AdminNavbar
      :title="navbarTitle"
      :subtitle="navbarSubtitle"
      :user-name="userName"
      :user-role="userRole"
      :search-placeholder="searchPlaceholder"
      :refresh-button-text="refreshButtonText"
      :loading="loading"
      @search="handleSearch"
      @refresh="handleRefresh"
    />
    
    <!-- Contenido principal -->
    <div class="p-6 sm:ml-64">
      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 mb-2">Gestión de Agricultores</h1>
            <p class="text-gray-600 text-lg">Administra todos los agricultores y fincas del sistema</p>
          </div>
        </div>
      </div>

      <!-- Contenido principal -->
      <main class="space-y-6">
        <!-- Estadísticas rápidas -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md hover:border-green-200 transition-all duration-200">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600">Total Agricultores</p>
                  <p class="text-2xl font-bold text-gray-900">{{ totalItems }}</p>
                </div>
              </div>
            </div>
            
            <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md hover:border-green-200 transition-all duration-200">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600">Total Fincas</p>
                  <p class="text-2xl font-bold text-gray-900">{{ getTotalFarms() }}</p>
                </div>
              </div>
            </div>
            
            <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md hover:border-green-200 transition-all duration-200">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600">Activos</p>
                  <p class="text-2xl font-bold text-gray-900">{{ getActiveFarmers() }}</p>
                </div>
              </div>
            </div>
            
            <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md hover:border-green-200 transition-all duration-200">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600">Área Total</p>
                  <p class="text-2xl font-bold text-gray-900">{{ getTotalArea() }} ha</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Barra de búsqueda -->
          <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <SearchBar 
              v-model="searchQuery"
              placeholder="Buscar agricultor por nombre, email o finca..."
            />
          </div>

          <!-- Tabla de agricultores -->
          <div class="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md hover:border-green-200 transition-all duration-200">
            <!-- Estado vacío -->
            <div v-if="filteredFarmers.length === 0" class="text-center py-12 px-6">
              <div class="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
              </div>
              <h3 class="text-lg font-medium text-gray-900 mb-2">No se encontraron agricultores</h3>
              <p class="text-gray-500 mb-6">
                {{ searchQuery || filters.region !== 'all' || filters.status !== 'all' 
                  ? 'Intenta ajustar los filtros o la búsqueda' 
                  : 'Comienza agregando tu primer agricultor' }}
              </p>
              <button 
                v-if="!searchQuery && filters.region === 'all' && filters.status === 'all'"
                @click="handleNewFarmer"
                class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
                Agregar Primer Agricultor
              </button>
            </div>

            <!-- Tabla con datos -->
            <DataTable 
              v-else
              :columns="tableColumns"
              :data="filteredFarmers"
            >
              <!-- Celda personalizada para Agricultor -->
              <template #cell-farmer="{ row }">
                <div class="flex items-center">
                  <div class="h-10 w-10 rounded-full bg-gradient-to-br from-green-100 to-green-200 flex items-center justify-center text-green-700 font-semibold text-sm border-2 border-green-100">
                    {{ row.initials }}
                  </div>
                  <div class="ml-3">
                    <div class="text-sm font-medium text-gray-900">{{ row.name }}</div>
                    <div class="text-xs text-gray-500">{{ row.email }}</div>
                  </div>
                </div>
              </template>

              <!-- Celda personalizada para Finca -->
              <template #cell-farm="{ row }">
                <div class="text-sm text-gray-900 font-medium">{{ row.farm }}</div>
                <div class="text-xs text-gray-500">{{ row.hectares }} hectáreas</div>
              </template>

              <!-- Celda personalizada para Estado -->
              <template #cell-status="{ row }">
                <span :class="getStatusClasses(row.status)" class="px-3 py-1.5 inline-flex text-xs leading-4 font-semibold rounded-full">
                  {{ row.status }}
                </span>
              </template>

              <!-- Celda personalizada para Acciones -->
              <template #cell-actions="{ row }">
                <div class="flex items-center space-x-3">
                  <button class="text-green-600 hover:text-green-700 hover:bg-green-50 p-1.5 rounded-md transition-all duration-200" title="Ver detalles">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                    </svg>
                  </button>
                  <button class="text-blue-600 hover:text-blue-700 hover:bg-blue-50 p-1.5 rounded-md transition-all duration-200" title="Editar">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </button>
                  <button class="text-red-600 hover:text-red-700 hover:bg-red-50 p-1.5 rounded-md transition-all duration-200" title="Eliminar">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                  </button>
                </div>
              </template>

              <!-- Paginación -->
              <template #pagination>
                <div class="bg-gray-50 px-6 py-4 border-t border-gray-200">
                  <Pagination 
                    :current-page="currentPage"
                    :total-pages="totalPages"
                    :total-items="totalItems"
                    :items-per-page="itemsPerPage"
                    @page-change="handlePageChange"
                  />
                </div>
              </template>
            </DataTable>
          </div>
        </main>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import AdminSidebar from '@/components/layout/AdminSidebar.vue';
import AdminNavbar from '@/components/layout/AdminNavbar.vue';
import SearchBar from '@/components/agricultores/SearchBar.vue';
import ActionButton from '@/components/agricultores/ActionButton.vue';
import FilterSelect from '@/components/agricultores/FilterSelect.vue';
import DataTable from '@/components/agricultores/DataTable.vue';
import Pagination from '@/components/agricultores/Pagination.vue';
import { useAuthStore } from '@/stores/auth';
import Swal from 'sweetalert2';

export default {
  name: 'AgricultoresView',
  components: {
    AdminSidebar,
    AdminNavbar,
    SearchBar,
    ActionButton,
    FilterSelect,
    DataTable,
    Pagination
  },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    // Estado reactivo
    const searchQuery = ref('');
    const currentPage = ref(1);
    const loading = ref(false);
    
    // Props para AdminSidebar y AdminNavbar
    const brandName = computed(() => 'CacaoScan');
    
    const userName = computed(() => {
      const user = authStore.user;
      if (user?.first_name && user?.last_name) {
        return `${user.first_name} ${user.last_name}`;
      }
      return user?.username || 'Administrador';
    });

    const userRole = computed(() => {
      return authStore.user?.is_superuser ? 'Administrador' : 'Usuario';
    });

    const navbarTitle = ref('Agricultores');
    const navbarSubtitle = ref('Gestión de agricultores y fincas');
    const searchPlaceholder = ref('Buscar agricultor por nombre, email o finca...');
    const refreshButtonText = ref('Actualizar');
    
    const filters = ref({
      region: '',
      status: ''
    });

    // Datos de ejemplo
    const farmers = ref([
      {
        id: 1,
        initials: 'CH',
        name: 'Camilo Hernandez',
        email: 'camilo@example.com',
        farm: 'Finca El Paraíso',
        hectares: '12 hectáreas',
        region: 'Santander',
        status: 'Activo'
      },
      {
        id: 2,
        initials: 'JA',
        name: 'Jeferson Alvarez',
        email: 'jeferson@example.com',
        farm: 'Finca Los Laureles',
        hectares: '8 hectáreas',
        region: 'Antioquia',
        status: 'Activo'
      },
      {
        id: 3,
        initials: 'CC',
        name: 'Cristian Camacho',
        email: 'cristian@example.com',
        farm: 'Finca El Mirador',
        hectares: '15 hectáreas',
        region: 'Huila',
        status: 'En revisión'
      },
      {
        id: 4,
        initials: 'JP',
        name: 'Juan Pablo Pérez',
        email: 'juanpablo@example.com',
        farm: 'Finca La Esperanza',
        hectares: '10 hectáreas',
        region: 'Nariño',
        status: 'Inactivo'
      }
    ]);

    // Configuración de la tabla
    const tableColumns = [
      { key: 'farmer', label: 'Agricultor' },
      { key: 'farm', label: 'Finca' },
      { key: 'region', label: 'Región' },
      { key: 'status', label: 'Estado' },
      { key: 'actions', label: 'Acciones', align: 'right' }
    ];

    // Opciones de filtros
    const regionOptions = [
      { value: '', label: 'Todas las regiones' },
      { value: 'Antioquia', label: 'Antioquia' },
      { value: 'Santander', label: 'Santander' },
      { value: 'Nariño', label: 'Nariño' },
      { value: 'Huila', label: 'Huila' }
    ];

    const statusOptions = [
      { value: '', label: 'Todos los estados' },
      { value: 'Activo', label: 'Activo' },
      { value: 'En Revisión', label: 'En Revisión' },
      { value: 'Inactivo', label: 'Inactivo' }
    ];

    // Computed properties
    const filteredFarmers = computed(() => {
      let filtered = farmers.value;
      
      // Filtrar por búsqueda
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        filtered = filtered.filter(farmer => 
          farmer.name.toLowerCase().includes(query) ||
          farmer.email.toLowerCase().includes(query) ||
          farmer.farm.toLowerCase().includes(query)
        );
      }
      
      // Filtrar por región
      if (filters.value.region) {
        filtered = filtered.filter(farmer => farmer.region === filters.value.region);
      }
      
      // Filtrar por estado
      if (filters.value.status) {
        filtered = filtered.filter(farmer => farmer.status === filters.value.status);
      }
      
      return filtered;
    });

    const totalItems = computed(() => filteredFarmers.value.length);
    const itemsPerPage = ref(4);
    const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value));

    // Métodos auxiliares para estadísticas
    const getTotalFarms = () => {
      return farmers.value.length;
    };

    const getActiveFarmers = () => {
      return farmers.value.filter(farmer => farmer.status === 'Activo').length;
    };

    const getTotalArea = () => {
      return farmers.value.reduce((total, farmer) => {
        const hectares = parseInt(farmer.hectares);
        return total + (isNaN(hectares) ? 0 : hectares);
      }, 0);
    };

    // Métodos para AdminSidebar y AdminNavbar
    const handleMenuClick = (menuItem) => {
      if (menuItem.route) {
        router.push(menuItem.route);
      }
    };

    const handleLogout = async () => {
      try {
        await authStore.logout();
        router.push('/login');
      } catch (error) {
        console.error('Error al cerrar sesión:', error);
      }
    };

    const handleSearch = (query) => {
      searchQuery.value = query;
    };

    const handleRefresh = () => {
      Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'success',
        title: 'Datos actualizados',
        showConfirmButton: false,
        timer: 2000
      });
    };

    const handleNewFarmer = () => {
      console.log('Nuevo agricultor');
      // Implementar lógica para crear nuevo agricultor
    };

    const applyFilters = () => {
      currentPage.value = 1; // Resetear a la primera página
      console.log('Aplicando filtros:', filters.value);
    };

    const handlePageChange = (page) => {
      currentPage.value = page;
    };

    const getStatusClasses = (status) => {
      switch (status) {
        case 'Activo':
          return 'bg-green-100 text-green-800';
        case 'En revisión':
          return 'bg-amber-100 text-amber-800';
        case 'Inactivo':
          return 'bg-red-100 text-red-800';
        default:
          return 'bg-gray-100 text-gray-800';
      }
    };

    // Lifecycle
    onMounted(() => {
      console.log('Vista Agricultores montada');
      checkScreenSize();
      window.addEventListener('resize', checkScreenSize);
    });

    const checkScreenSize = () => {
      if (window.innerWidth <= 768) {
        sidebarCollapsed.value = true;
        localStorage.setItem('sidebarCollapsed', 'true');
      }
    };

    return {
      // Estado
      searchQuery,
      currentPage,
      loading,
      
      // Props para componentes
      brandName,
      userName,
      userRole,
      navbarTitle,
      navbarSubtitle,
      searchPlaceholder,
      refreshButtonText,
      
      // Filtros
      filters,
      
      // Datos
      farmers,
      tableColumns,
      regionOptions,
      statusOptions,
      filteredFarmers,
      totalItems,
      itemsPerPage,
      totalPages,
      
      // Métodos
      handleMenuClick,
      handleLogout,
      handleSearch,
      handleRefresh,
      handleNewFarmer,
      applyFilters,
      handlePageChange,
      getStatusClasses,
      getTotalFarms,
      getActiveFarmers,
      getTotalArea
    };
  }
};
</script>

<style scoped>
/* Estilos específicos para la vista de agricultores */
.min-h-screen {
  min-height: 100vh;
}

.h-screen {
  height: 100vh;
}

/* Asegurar que el contenido principal no se desborde */
.min-w-0 {
  min-width: 0;
}

/* Eliminar espacio blanco excesivo */
.flex-1 {
  flex: 1 1 0%;
}

/* Asegurar que el contenido principal ocupe toda la altura disponible */
main {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

/* Controlar el overflow */
.overflow-hidden {
  overflow: hidden;
}

.overflow-y-auto {
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* Layout principal del dashboard */
.dashboard-layout {
  display: flex;
  height: 100vh;
  width: 100%;
}

/* Contenido principal del dashboard */
.dashboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
  transition: all 0.3s ease;
}

/* Asegurar que el contenido se ajuste correctamente */
.dashboard-content > * {
  width: 100%;
}

/* Layout específico para la vista de agricultores */
.bg-gray-50 {
  background-color: #f9fafb;
}

/* Asegurar que el sidebar y contenido principal se alineen correctamente */
.flex.h-screen {
  height: 100vh;
  max-height: 100vh;
}

/* Estilos para cuando el sidebar está colapsado */
.main-expanded {
  margin-left: 0;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 0;
}

/* Estilos para cuando el sidebar está expandido */
.main-collapsed {
  margin-left: 0;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 0;
}

/* Transición suave para el contenido principal */
.flex-1.flex.flex-col {
  transition: all 0.3s ease;
}

/* Asegurar que el contenido se ajuste correctamente */
.flex-1 {
  min-width: 0;
  flex: 1;
  width: 100%;
}

/* Mejoras de responsividad */
@media (max-width: 768px) {
  .p-4 {
    padding: 1rem;
  }
  
  .md\:p-6 {
    padding: 1.5rem;
  }
  
  .mb-6 {
    margin-bottom: 1rem;
  }
  
  .mb-8 {
    margin-bottom: 1.5rem;
  }
  
  /* Ajustar el grid en tablets */
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  /* Reducir padding inferior en móviles */
  .pb-0 {
    padding-bottom: 0;
  }
  
  /* Asegurar que el layout se ajuste en móviles */
  .h-screen {
    height: 100vh;
    min-height: 100vh;
  }
  
  /* Ajustar el overflow en móviles */
  .overflow-y-auto {
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  
  .overflow-y-auto::-webkit-scrollbar {
    display: none;
  }
  
  /* Asegurar que el sidebar esté colapsado en móviles */
  .sidebar-collapsed {
    width: 70px;
  }
  
  /* Ajustar el contenido principal en móviles */
  .main-expanded,
  .main-collapsed {
    margin-left: 0;
    flex: 1;
    min-width: 0;
  }
}

@media (max-width: 640px) {
  .p-4 {
    padding: 0.75rem;
  }
  
  .mb-6 {
    margin-bottom: 1rem;
  }
  
  .mb-8 {
    margin-bottom: 1.5rem;
  }
  
  .gap-4 {
    gap: 0.75rem;
  }
  
  /* Forzar una columna en móviles */
  .md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  /* Eliminar padding inferior en pantallas pequeñas */
  .pb-0 {
    padding-bottom: 0;
  }
  
  /* Ajustar el contenido principal en pantallas pequeñas */
  .main-expanded,
  .main-collapsed {
    margin-left: 0;
    flex: 1;
    min-width: 0;
  }
}

@media (max-width: 480px) {
  .p-4 {
    padding: 0.5rem;
  }
  
  .mb-6 {
    margin-bottom: 0.5rem;
  }
  
  .mb-8 {
    margin-bottom: 0.75rem;
  }
  
  .gap-4 {
    gap: 0.5rem;
  }
  
  /* Una sola columna en pantallas muy pequeñas */
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  /* Ajustar espaciado de botones en móviles */
  .flex.gap-2 {
    gap: 0.5rem;
  }
  
  /* Eliminar padding inferior en pantallas muy pequeñas */
  .pb-0 {
    padding-bottom: 0;
  }
  
  /* Asegurar que el layout se ajuste en pantallas muy pequeñas */
  .h-screen {
    height: 100vh;
    min-height: 100vh;
  }
  
  /* Ajustar el contenido para pantallas muy pequeñas */
  main {
    padding: 0.5rem;
  }
  
  /* Reducir espaciado en pantallas muy pequeñas */
  .mb-4 {
    margin-bottom: 0.5rem;
  }
  
  /* Asegurar que el sidebar esté completamente colapsado en pantallas muy pequeñas */
  .sidebar-collapsed {
    width: 60px;
  }
  
  /* Ajustar el contenido principal en pantallas muy pequeñas */
  .main-expanded,
  .main-collapsed {
    margin-left: 0;
    flex: 1;
    min-width: 0;
  }
}

/* Transiciones suaves */
* {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Mejoras para dispositivos táctiles */
@media (hover: none) and (pointer: coarse) {
  .min-h-screen {
    min-height: 100vh;
  }
  
  /* Asegurar que los botones tengan el tamaño mínimo táctil */
  button {
    min-height: 44px;
    min-width: 44px;
  }
}

/* Responsive para pantallas muy grandes */
@media (min-width: 1280px) {
  .lg\:p-8 {
    padding: 2rem;
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

/* Mejoras para orientación landscape en móviles */
@media (max-width: 768px) and (orientation: landscape) {
  .p-4 {
    padding: 0.75rem;
  }
  
  .mb-6 {
    margin-bottom: 1rem;
  }
  
  .mb-8 {
    margin-bottom: 1.5rem;
  }
}

/* Animaciones de entrada */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

main {
  animation: fadeIn 0.5s ease-out;
}

/* Mejoras para accesibilidad */
*:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Estados de carga */
.loading {
  opacity: 0.6;
  pointer-events: none;
}

/* Mejoras para tablas responsivas */
@media (max-width: 640px) {
  .grid-cols-1 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  /* Ajustar el layout de filtros en móviles */
  .flex-col.sm\:flex-row {
    flex-direction: column;
  }
  
  .items-start.sm\:items-center {
    align-items: flex-start;
  }
  
  .justify-between {
    justify-content: flex-start;
  }
  
  .flex.gap-2 {
    margin-top: 1rem;
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  /* Ajustar espaciado en pantallas muy pequeñas */
  .space-y-1 > * + * {
    margin-top: 0.25rem;
  }
  
  .space-y-1 > * + * {
    margin-top: 0.25rem;
  }
}

/* Mejoras para el scroll en móviles */
@media (max-width: 640px) {
  .overflow-x-auto {
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
  }
}

/* Optimizaciones para pantallas de alta densidad */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .bg-white {
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
  }
}

/* Mejoras para dispositivos con pantallas pequeñas y alta densidad */
@media (max-width: 640px) and (-webkit-min-device-pixel-ratio: 2) {
  .text-sm {
    font-size: 0.8125rem;
  }
  
  .text-xs {
    font-size: 0.6875rem;
  }
}

/* Mejoras de responsividad adicionales para la tabla */
@media (max-width: 640px) {
  .chart-container {
    min-height: 250px;
  }
}

@media (max-width: 480px) {
  .chart-container {
    min-height: 300px;
  }
}

/* Transiciones suaves para mejor UX */
* {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Mejoras para dispositivos táctiles */
@media (hover: none) and (pointer: coarse) {
  button, a {
    min-height: 44px;
    min-width: 44px;
  }
  
  .table-responsive {
    -webkit-overflow-scrolling: touch;
  }
}

/* Optimizaciones para pantallas pequeñas */
@media (max-width: 768px) {
  .sidebar-collapsed {
    width: 4rem;
  }
  
  .main-content-expanded {
    margin-left: 4rem;
  }
}
</style>
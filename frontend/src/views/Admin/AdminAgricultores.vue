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
                @click="handleNewFarmer"
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
          :filtered-farmers="filteredFarmers"
          :search-query="searchQuery"
          :filters="filters"
          :table-columns="tableColumns"
          :current-page="currentPage"
          :total-pages="totalPages"
          :total-items="totalItems"
          :items-per-page="itemsPerPage"
          @new-farmer="handleNewFarmer"
          @page-change="handlePageChange"
        />
        </main>
    </div>

    <!-- Modal para crear agricultor -->
    <CreateFarmerModal 
      ref="createFarmerModalRef"
      @farmer-created="handleFarmerCreated"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter }                from 'vue-router';
import AdminSidebar                 from '@/components/layout/Common/Sidebar.vue';
import FarmersStatsCards            from '@/components/admin/AdminAgricultorComponents/FarmersStatsCards.vue';
import FarmersSearchBar             from '@/components/admin/AdminAgricultorComponents/FarmersSearchBar.vue';
import FarmersTable                 from '@/components/admin/AdminAgricultorComponents/FarmersTable.vue';
import CreateFarmerModal            from '@/components/admin/AdminAgricultorComponents/CreateFarmerModal.vue';
import { useAuthStore }             from '@/stores/auth';
import { getFincas, getFincaStats } from '@/services/fincasApi';
import Swal                         from 'sweetalert2';

export default {
  name: 'AdminAgricultores',
  components: { AdminSidebar, FarmersStatsCards, FarmersSearchBar, FarmersTable, CreateFarmerModal },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    // Estado reactivo
    const searchQuery = ref('');
    const currentPage = ref(1);
    const loading = ref(false);
    const allFincas = ref([]);
    
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
      const role = authStore.userRole || 'Usuario'
      // Normalize role for sidebar - Backend returns: 'admin', 'analyst', or 'farmer'
      if (role === 'admin') return 'admin'
      if (role === 'farmer') return 'agricultor'
      return 'admin' // Default to admin
    })

    // Sidebar collapse state
    const isSidebarCollapsed = ref(false);

    const toggleSidebarCollapse = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value;
      localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value);
    };

    const navbarTitle = ref('Agricultores');
    const navbarSubtitle = ref('Gestión de agricultores y fincas');
    const searchPlaceholder = ref('Buscar agricultor por nombre, email o finca...');
    const refreshButtonText = ref('Actualizar');
    
    const filters = ref({
      region: '',
      status: ''
    });

    // Datos reales cargados desde backend
    const farmers = ref([]);

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

    // Función para cargar agricultores desde el backend
    const loadFarmers = async () => {
      loading.value = true;
      try {
        // Obtener todas las fincas del backend
        const response = await getFincas({});
        
        // Extraer información única de agricultores
        const agricultoresMap = new Map();
        
        for (const finca of response.results || []) {
          const agricultor = finca.agricultor;
          
          // Validar que el agricultor existe y tiene id
          if (!agricultor || !agricultor.id) {
            console.warn('Finca sin agricultor válido:', finca);
            continue;
          }
          
          if (!agricultoresMap.has(agricultor.id)) {
            // Obtener iniciales
            const names = agricultor.first_name?.split(' ') || agricultor.username?.split(' ') || [];
            const initials = names.length >= 2 
              ? `${names[0].charAt(0)}${names[1].charAt(0)}`.toUpperCase()
              : agricultor.username?.substring(0, 2).toUpperCase() || 'AA';
            
            agricultoresMap.set(agricultor.id, {
              id: agricultor.id,
              initials,
              name: `${agricultor.first_name || ''} ${agricultor.last_name || ''}`.trim() || agricultor.username,
              email: agricultor.email,
              farm: finca.nombre,
              hectares: `${finca.hectareas} hectáreas`,
              region: finca.departamento,
              status: finca.activa ? 'Activo' : 'Inactivo',
              fincas: [finca]
            });
          } else {
            // Si el agricultor ya existe, agregar finca a su lista
            const existingFarmer = agricultoresMap.get(agricultor.id);
            if (existingFarmer && existingFarmer.fincas) {
              existingFarmer.fincas.push(finca);
            }
          }
        }
        
        farmers.value = Array.from(agricultoresMap.values());
        allFincas.value = response.results || [];
      } catch (error) {
        console.error('Error cargando agricultores:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron cargar los agricultores',
          confirmButtonColor: '#10b981'
        });
      } finally {
        loading.value = false;
      }
    };

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
      return allFincas.value.length;
    };

    const getActiveFarmers = () => {
      return farmers.value.filter(farmer => farmer.status === 'Activo').length;
    };

    const getTotalArea = () => {
      return allFincas.value.reduce((total, finca) => {
        return total + parseFloat(finca.hectareas || 0);
      }, 0).toFixed(1);
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

    const handleRefresh = async () => {
      await loadFarmers();
      Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'success',
        title: 'Datos actualizados',
        showConfirmButton: false,
        timer: 2000
      });
    };

    // Referencia al modal
    const createFarmerModalRef = ref(null);

    const handleNewFarmer = () => {
      if (createFarmerModalRef.value) {
        createFarmerModalRef.value.openModal();
      }
    };

    const handleFarmerCreated = async (farmerData) => {
      // Recargar la lista de agricultores
      await loadFarmers();
      
      Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'success',
        title: 'Agricultor creado exitosamente',
        showConfirmButton: false,
        timer: 2000
      });
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
    onMounted(async () => {
      console.log('Vista Agricultores montada');
      checkScreenSize();
      window.addEventListener('resize', checkScreenSize);
      await loadFarmers();
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
      isSidebarCollapsed,
      toggleSidebarCollapse,
      allFincas,
      createFarmerModalRef,
      
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
      getTotalArea,
      loadFarmers
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
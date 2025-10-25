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
      <div class="analysis-view">
        <!-- Contenido principal -->
        <main class="flex-1 p-4 md:p-6 lg:p-8 pb-0 overflow-y-auto">
          <!-- Filtros y controles -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <div class="flex gap-4 items-center justify-between">
              <div class="flex gap-4">
                <FilterSelect 
                  id="agricultor"
                  label="Agricultor"
                  v-model="filters.agricultor"
                  :options="farmerOptions"
                />
                <FilterSelect 
                  id="resultado"
                  label="Resultado"
                  v-model="filters.resultado"
                  :options="resultOptions"
                />
                <DateInput 
                  id="fecha"
                  label="Fecha"
                  v-model="filters.fecha"
                />
              </div>
              
              <div class="flex gap-2">
                <ActionButton 
                  label="Aplicar Filtros"
                  short-label="Filtrar"
                  variant="secondary"
                  icon="FunnelIcon"
                  @click="applyFilters"
                />
                <ActionButton 
                  label="Analizar Imagen"
                  short-label="+ Imagen"
                  variant="primary"
                  icon="PlusIcon"
                  @click="handleNewAnalysis"
                />
              </div>
            </div>
          </div>
          
          <!-- Tarjetas de estadísticas -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-4 md:mb-6">
            <StatsCard 
              title="Análisis Aceptados"
              :value="stats.aceptados"
              :change="stats.aceptadosChange"
              icon="CheckIcon"
              variant="success"
            />
            <StatsCard 
              title="Análisis Condicionales"
              :value="stats.condicionales"
              :change="stats.condicionalesChange"
              icon="ExclamationIcon"
              variant="warning"
            />
            <StatsCard 
              title="Análisis Rechazados"
              :value="stats.rechazados"
              :change="stats.rechazadosChange"
              icon="XIcon"
              variant="danger"
            />
            <StatsCard 
              title="Total Análisis"
              :value="stats.total"
              :change="stats.totalChange"
              icon="ChartBarIcon"
              variant="info"
            />
          </div>
          
          <!-- Tabla de análisis -->
          <div class="flex-1 min-h-0">
            <AnalysisTable 
              :analyses="filteredAnalyses"
              :total-items="totalItems"
            />
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Swal from 'sweetalert2';
import { useAuthStore } from '@/stores/auth';
import AdminSidebar from '@/components/layout/AdminSidebar.vue';
import AdminNavbar from '@/components/layout/AdminNavbar.vue';
import PageHeader from '@/components/analisis/PageHeader.vue';
import SearchBar from '@/components/analisis/SearchBar.vue';
import ActionButton from '@/components/analisis/ActionButton.vue';
import FilterSelect from '@/components/analisis/FilterSelect.vue';
import DateInput from '@/components/analisis/DateInput.vue';
import StatsCard from '@/components/analisis/StatsCard.vue';
import AnalysisTable from '@/components/analisis/AnalysisTable.vue';

export default {
  name: 'AnalisisView',
  components: {
    AdminSidebar,
    AdminNavbar,
    PageHeader,
    SearchBar,
    ActionButton,
    FilterSelect,
    DateInput,
    StatsCard,
    AnalysisTable
  },
  setup() {
    // Inicializar router y stores
    const router = useRouter();
    const authStore = useAuthStore();
    
    // Sidebar properties
    const brandName = computed(() => 'CacaoScan');
    const userName = computed(() => {
      const user = authStore.user;
      return user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username : 'Usuario';
    });
    const userRole = computed(() => {
      const user = authStore.user;
      if (user?.is_superuser) return 'Superadministrador';
      if (user?.is_staff) return 'Administrador';
      return 'Usuario';
    });

    // Navbar properties
    const navbarTitle = ref('Análisis de Calidad');
    const navbarSubtitle = ref('Gestión de análisis de calidad de cacao');
    const searchPlaceholder = ref('Buscar análisis...');
    const refreshButtonText = ref('Actualizar');
    
    // Estado reactivo
    const searchQuery = ref('');
    const loading = ref(false);
    
    const filters = ref({
      agricultor: '',
      resultado: '',
      fecha: ''
    });

    // Datos de análisis
    const analyses = ref([
      {
        id: '#AN-001',
        farmerInitials: 'CH',
        farmerName: 'Camilo Hernandez',
        batch: 'Lote #101',
        date: '15/06/2023',
        status: 'Aceptado',
        quality: 87
      },
      {
        id: '#AN-002',
        farmerInitials: 'JA',
        farmerName: 'Jeferson Alvarez',
        batch: 'Lote #102',
        date: '18/06/2023',
        status: 'Condicional',
        quality: 65
      },
      {
        id: '#AN-003',
        farmerInitials: 'CC',
        farmerName: 'Cristian Camacho',
        batch: 'Lote #103',
        date: '20/06/2023',
        status: 'Rechazado',
        quality: 35
      },
      {
        id: '#AN-004',
        farmerInitials: 'JP',
        farmerName: 'Juan Pablo Pérez',
        batch: 'Lote #104',
        date: '22/06/2023',
        status: 'Aceptado',
        quality: 92
      }
    ]);

    // Opciones para filtros
    const farmerOptions = ref([
      { value: '', label: 'Todos los agricultores' },
      { value: 'camilo', label: 'Camilo Hernandez' },
      { value: 'jeferson', label: 'Jeferson Alvarez' },
      { value: 'cristian', label: 'Cristian Camacho' },
      { value: 'juan', label: 'Juan Pablo Pérez' }
    ]);

    const resultOptions = ref([
      { value: '', label: 'Todos los resultados' },
      { value: 'aceptado', label: 'Aceptado' },
      { value: 'condicional', label: 'Condicional' },
      { value: 'rechazado', label: 'Rechazado' }
    ]);

    // Estadísticas
    const stats = ref({
      aceptados: 124,
      aceptadosChange: 8,
      condicionales: 45,
      condicionalesChange: 3,
      rechazados: 12,
      rechazadosChange: 2,
      total: 181,
      totalChange: 5
    });

    // Computed properties
    const filteredAnalyses = computed(() => {
      let filtered = analyses.value;

      // Filtro por búsqueda
      if (searchQuery.value) {
        filtered = filtered.filter(analysis => 
          analysis.farmerName.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          analysis.id.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          analysis.batch.toLowerCase().includes(searchQuery.value.toLowerCase())
        );
      }

      // Filtro por agricultor
      if (filters.value.agricultor) {
        filtered = filtered.filter(analysis => 
          analysis.farmerName.toLowerCase().includes(filters.value.agricultor.toLowerCase())
        );
      }

      // Filtro por resultado
      if (filters.value.resultado) {
        filtered = filtered.filter(analysis => 
          analysis.status.toLowerCase() === filters.value.resultado.toLowerCase()
        );
      }

      // Filtro por fecha
      if (filters.value.fecha) {
        filtered = filtered.filter(analysis => 
          analysis.date === filters.value.fecha
        );
      }

      return filtered;
    });

    const totalItems = computed(() => filteredAnalyses.value.length);

    // Métodos
    const handleNewAnalysis = () => {
      console.log('Navegando a predicción de imagen');
      router.push({ name: 'Prediction' });
    };

    const applyFilters = () => {
      console.log('Aplicando filtros:', filters.value);
      loading.value = true;
      // Simular carga de datos
      setTimeout(() => {
        loading.value = false;
      }, 1000);
    };

    // Sidebar event handlers
    const handleMenuClick = (menuItem) => {
      console.log('Menu clicked:', menuItem);
      router.push(menuItem.route);
    };

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
      });

      if (result.isConfirmed) {
        await authStore.logout();
        router.push('/login');
      }
    };

    // Navbar event handlers
    const handleSearch = (query) => {
      searchQuery.value = query;
    };

    const handleRefresh = () => {
      loading.value = true;
      // Simular recarga de datos
      setTimeout(() => {
        loading.value = false;
        Swal.fire({
          icon: 'success',
          title: 'Datos actualizados',
          toast: true,
          position: 'top-end',
          showConfirmButton: false,
          timer: 2000
        });
      }, 1000);
    };

    // Lifecycle
    onMounted(() => {
      console.log('Vista de análisis montada');
    });

    return {
      // Sidebar & Navbar
      brandName,
      userName,
      userRole,
      navbarTitle,
      navbarSubtitle,
      searchPlaceholder,
      refreshButtonText,
      
      // Estado
      searchQuery,
      loading,
      
      // Router
      router,
      
      // Filtros
      filters,
      
      // Datos
      analyses,
      farmerOptions,
      resultOptions,
      stats,
      filteredAnalyses,
      totalItems,
      
      // Métodos
      handleNewAnalysis,
      applyFilters,
      handleMenuClick,
      handleLogout,
      handleSearch,
      handleRefresh
    };
  }
};
</script>

<style scoped>
/* Estilos específicos para la vista de análisis */
.analysis-view {
  padding: 0;
  background-color: transparent;
  min-height: auto;
}

.min-h-screen {
  min-height: 100vh;
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

/* Asegurar que el contenido se ajuste correctamente */
.flex.flex-col {
  display: flex;
  flex-direction: column;
}

/* Asegurar que el contenido se ajuste al viewport */
.min-h-0 {
  min-height: 0;
}

/* Layout específico para la vista de análisis */
.bg-gray-50 {
  background-color: #f9fafb;
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
    margin-bottom: 0.75rem;
  }
  
  .mb-8 {
    margin-bottom: 1rem;
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
  .main-expanded {
    margin-left: 0;
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
</style>
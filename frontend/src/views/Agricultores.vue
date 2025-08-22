<template>
  <div class="min-h-screen bg-gray-50 flex pb-8">
    <!-- Sidebar -->
    <AdminSidebar 
      user-initials="AD"
      user-name="Admin"
      user-role="Ver perfil"
    />

    <!-- Main Content -->
    <main class="flex-1 ml-16 md:ml-64 transition-all duration-300">
      <!-- Header -->
      <PageHeader 
        title="Agricultores"
        subtitle="Gestión de agricultores y fincas"
      />

      <!-- Contenido principal -->
      <div class="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8 py-4 md:py-8">
        <!-- Barra de acciones -->
        <div class="mb-4 md:mb-6">
          <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-3 sm:space-y-0">
            <div>
              <h2 class="text-lg md:text-xl font-semibold text-gray-800">Listado de Agricultores</h2>
              <p class="text-xs md:text-sm text-gray-500">Gestiona los agricultores registrados en el sistema</p>
            </div>
            <div class="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
              <SearchBar 
                v-model="searchQuery"
                placeholder="Buscar agricultor..."
              />
              <ActionButton 
                label="Nuevo Agricultor"
                short-label="+ Nuevo"
                variant="primary"
                @click="handleNewFarmer"
              />
            </div>
          </div>
        </div>

        <!-- Filtros -->
        <div class="mb-4 md:mb-6 bg-white p-3 md:p-4 rounded-lg shadow-sm border border-gray-200">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
            <FilterSelect 
              id="region"
              label="Región"
              v-model="filters.region"
              :options="regionOptions"
            />
            
            <FilterSelect 
              id="status"
              label="Estado"
              v-model="filters.status"
              :options="statusOptions"
            />
            
            <div class="sm:col-span-2 lg:col-span-1 flex items-end">
              <ActionButton 
                label="Aplicar Filtros"
                variant="secondary"
                @click="applyFilters"
              />
            </div>
          </div>
        </div>

        <!-- Tabla de agricultores -->
        <DataTable 
          :columns="tableColumns"
          :data="filteredFarmers"
        >
          <!-- Celda personalizada para Agricultor -->
          <template #cell-farmer="{ row }">
            <div class="flex items-center">
              <div class="h-8 w-8 md:h-10 md:w-10 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-medium text-sm md:text-base">
                {{ row.initials }}
              </div>
              <div class="ml-2 md:ml-4">
                <div class="text-xs md:text-sm font-medium text-gray-900">{{ row.name }}</div>
                <div class="text-xs md:text-sm text-gray-500">{{ row.email }}</div>
              </div>
            </div>
          </template>

          <!-- Celda personalizada para Finca -->
          <template #cell-farm="{ row }">
            <div class="text-xs md:text-sm text-gray-900">{{ row.farm }}</div>
            <div class="text-xs md:text-sm text-gray-500">{{ row.hectares }}</div>
          </template>

          <!-- Celda personalizada para Estado -->
          <template #cell-status="{ row }">
            <span :class="getStatusClasses(row.status)" class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full">
              {{ row.status }}
            </span>
          </template>

          <!-- Celda personalizada para Acciones -->
          <template #cell-actions="{ row }">
            <div class="flex flex-col sm:flex-row sm:space-x-2 space-y-1 sm:space-y-0">
              <a href="#" class="text-green-600 hover:text-green-900 transition-colors duration-200">Ver</a>
              <a href="#" class="text-blue-600 hover:text-blue-900 transition-colors duration-200">Editar</a>
              <a href="#" class="text-red-600 hover:text-red-900 transition-colors duration-200">Eliminar</a>
            </div>
          </template>

          <!-- Paginación -->
          <template #pagination>
            <Pagination 
              :current-page="currentPage"
              :total-pages="totalPages"
              :total-items="totalItems"
              :items-per-page="itemsPerPage"
              @page-change="handlePageChange"
            />
          </template>
        </DataTable>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import AdminSidebar from '@/components/agricultores/AdminSidebar.vue';
import PageHeader from '@/components/agricultores/PageHeader.vue';
import SearchBar from '@/components/agricultores/SearchBar.vue';
import ActionButton from '@/components/agricultores/ActionButton.vue';
import FilterSelect from '@/components/agricultores/FilterSelect.vue';
import DataTable from '@/components/agricultores/DataTable.vue';
import Pagination from '@/components/agricultores/Pagination.vue';

export default {
  name: 'AgricultoresView',
  components: {
    AdminSidebar,
    PageHeader,
    SearchBar,
    ActionButton,
    FilterSelect,
    DataTable,
    Pagination
  },
  setup() {
    // Estado reactivo
    const searchQuery = ref('');
    const currentPage = ref(1);
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

      // Filtro por búsqueda
      if (searchQuery.value) {
        filtered = filtered.filter(farmer => 
          farmer.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          farmer.email.toLowerCase().includes(searchQuery.value.toLowerCase())
        );
      }

      // Filtro por región
      if (filters.value.region) {
        filtered = filtered.filter(farmer => farmer.region === filters.value.region);
      }

      // Filtro por estado
      if (filters.value.status) {
        filtered = filtered.filter(farmer => farmer.status === filters.value.status);
      }

      return filtered;
    });

    const totalItems = computed(() => filteredFarmers.value.length);
    const itemsPerPage = 4;
    const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage));

    // Métodos
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
          return 'bg-yellow-100 text-yellow-800';
        case 'Inactivo':
          return 'bg-red-100 text-red-800';
        default:
          return 'bg-gray-100 text-gray-800';
      }
    };

    return {
      searchQuery,
      currentPage,
      filters,
      farmers,
      tableColumns,
      regionOptions,
      statusOptions,
      filteredFarmers,
      totalItems,
      itemsPerPage,
      totalPages,
      handleNewFarmer,
      applyFilters,
      handlePageChange,
      getStatusClasses
    };
  }
};
</script>

<style scoped>
/* Mejoras de responsividad adicionales */
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